import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');
const WORKTREE_SCRIPT = path.join(REPO_ROOT, 'scripts/worktree.mjs');

let tempDir;

function runScript(args = [], cwd = tempDir) {
  return spawnSync(process.execPath, [WORKTREE_SCRIPT, ...args], {
    cwd,
    encoding: 'utf8',
  });
}

function runGit(args, cwd = tempDir) {
  return spawnSync('git', args, {
    cwd,
    encoding: 'utf8',
  });
}

beforeEach(() => {
  tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scaffold-wt-test-'));
  // Initialize a real git repo for isolated worktree testing
  runGit(['init', '-b', 'main']);
  runGit(['config', 'user.name', 'Scaffold Test']);
  runGit(['config', 'user.email', 'test@scaffold.ai']);
  fs.writeFileSync(path.join(tempDir, 'README.md'), '# Test Repo\n');
  runGit(['add', '.']);
  runGit(['commit', '-m', 'Initial commit']);
});

afterEach(() => {
  if (tempDir && fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

describe('worktree.mjs', () => {
  test('prints help documentation on --help', () => {
    const res = runScript(['--help']);
    assert.equal(res.status, 0);
    assert.match(res.stdout, /Scaffold\.ai Worktree Manager/);
    assert.match(res.stdout, /list/);
    assert.match(res.stdout, /add <name>/);
    assert.match(res.stdout, /remove <name>/);
  });

  test('lists root checkout in clean repository', () => {
    const res = runScript(['list']);
    assert.equal(res.status, 0);
    assert.match(res.stdout, /Active Git Worktrees/);
    assert.match(res.stdout, /main/);
  });

  test('rejects add without a worktree name', () => {
    const res = runScript(['add']);
    assert.notEqual(res.status, 0);
    assert.match(res.stderr, /Worktree name is required/);
  });

  test('creates new worktree and branch in .worktrees/<name>', () => {
    const res = runScript(['add', 'feature-auth']);
    assert.equal(res.status, 0, `Failed to add worktree: ${res.stderr}`);
    assert.match(res.stdout, /Worktree created successfully/);
    assert.match(res.stdout, /feat\/feature-auth/);

    const wtDir = path.join(tempDir, '.worktrees/feature-auth');
    assert.ok(fs.existsSync(wtDir), 'Worktree directory should exist');

    // Verify git branch in the worktree
    const branchRes = runGit(['symbolic-ref', '--short', 'HEAD'], wtDir);
    assert.equal(branchRes.stdout.trim(), 'feat/feature-auth');
  });

  test('refuses to add worktree if directory already exists', () => {
    fs.mkdirSync(path.join(tempDir, '.worktrees/duplicate'), { recursive: true });
    const res = runScript(['add', 'duplicate']);
    assert.notEqual(res.status, 0);
    assert.match(res.stderr, /Destination directory already exists/);
  });

  test('rejects remove without a target name', () => {
    const res = runScript(['remove']);
    assert.notEqual(res.status, 0);
    assert.match(res.stderr, /Worktree name or path is required/);
  });

  test('rejects remove when worktree is not found', () => {
    const res = runScript(['remove', 'non-existent']);
    assert.notEqual(res.status, 0);
    assert.match(res.stderr, /No active worktree found/);
  });

  test('safely removes clean worktree', () => {
    runScript(['add', 'cleanup-test']);
    const wtDir = path.join(tempDir, '.worktrees/cleanup-test');
    assert.ok(fs.existsSync(wtDir));

    const removeRes = runScript(['remove', 'cleanup-test']);
    assert.equal(removeRes.status, 0, `Remove failed: ${removeRes.stderr}`);
    assert.match(removeRes.stdout, /removed successfully/);
    assert.ok(!fs.existsSync(wtDir), 'Directory should be removed');
  });

  test('refuses to remove dirty worktree without --force', () => {
    runScript(['add', 'dirty-test']);
    const wtDir = path.join(tempDir, '.worktrees/dirty-test');
    fs.writeFileSync(path.join(wtDir, 'dirty.txt'), 'uncommitted changes');

    const removeRes = runScript(['remove', 'dirty-test']);
    assert.notEqual(removeRes.status, 0);
    assert.match(removeRes.stderr, /contains uncommitted changes/);
    assert.ok(fs.existsSync(wtDir), 'Directory should still exist');

    // Now remove with --force
    const forceRes = runScript(['remove', 'dirty-test', '--force']);
    assert.equal(forceRes.status, 0, `Force remove failed: ${forceRes.stderr}`);
    assert.match(forceRes.stdout, /removed successfully/);
    assert.ok(!fs.existsSync(wtDir), 'Directory should be removed after --force');
  });
});
