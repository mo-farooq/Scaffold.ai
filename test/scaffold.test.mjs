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
const INIT_SCRIPT = path.join(REPO_ROOT, 'skills/scaffold/scripts/init-scaffold.mjs');
const VERIFY_SCRIPT = path.join(REPO_ROOT, 'skills/scaffold/scripts/verify-gate.mjs');

let tempDir;

function runScript(scriptPath, args = [], cwd = tempDir) {
  return spawnSync(process.execPath, [scriptPath, ...args], {
    cwd,
    encoding: 'utf8',
  });
}

beforeEach(() => {
  tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scaffold-test-'));
});

afterEach(() => {
  if (tempDir && fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

describe('init-scaffold.mjs', () => {
  const tracks = ['redis', 'git', 'http', 'sqlite', 'docker'];

  for (const track of tracks) {
    test(`initializes curated track "${track}" cleanly`, () => {
      const res = runScript(INIT_SCRIPT, ['--track', track]);
      assert.equal(res.status, 0, `Failed to init track ${track}: ${res.stderr}`);

      const progressPath = path.join(tempDir, 'PROGRESS.md');
      assert.ok(fs.existsSync(progressPath), 'PROGRESS.md should exist');

      const content = fs.readFileSync(progressPath, 'utf8');
      assert.match(content, new RegExp(`Track: ${track}`, 'i'));
      assert.match(content, /Milestone 1/);
      assert.match(content, /▶ \*\*\[ACTIVE\]\*\*/);
      assert.match(content, /## 🧠 Mental Model Matrix/);
      assert.match(content, /🔴 Not reviewed/);
      assert.match(content, /## 🚀 Start Here/);
      assert.match(content, /\*\*Your next action\*\*/);
      assert.match(content, /\*\*You own\*\*/);
      assert.match(content, /\*\*The agent owns\*\*/);

      // Verify workspace guardrail was copied
      const rulePath = path.join(tempDir, '.agents/rules/scaffold-guardrails.md');
      assert.ok(fs.existsSync(rulePath), '.agents/rules/scaffold-guardrails.md should exist');
    });
  }

  test('initializes custom ideas with default milestones', () => {
    const idea = 'Build a distributed task queue in Go';
    const res = runScript(INIT_SCRIPT, ['--idea', idea]);
    assert.equal(res.status, 0, res.stderr);

    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');
    assert.match(progress, /Build a distributed task queue in Go/);
    assert.match(progress, /Milestone 1.*Core Architecture/);
    assert.match(progress, /Milestone 4.*Persistence/);
  });

  test('initializes custom ideas with explicit custom milestones', () => {
    const idea = 'Learn Python with a CLI task manager';
    const milestones = 'CLI flags & models|Task state transitions|JSON persistence';
    const res = runScript(INIT_SCRIPT, ['--idea', idea, '--milestones', milestones]);
    assert.equal(res.status, 0, res.stderr);

    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');
    assert.match(progress, /Learn Python with a CLI task manager/);
    assert.match(progress, /Milestone 1.*CLI flags & models/);
    assert.match(progress, /Milestone 2.*Task state transitions/);
    assert.match(progress, /Milestone 3.*JSON persistence/);
    assert.doesNotMatch(progress, /Milestone 4/);
  });

  test('supports --hardcore mode flag', () => {
    const res = runScript(INIT_SCRIPT, ['--track', 'redis', '--hardcore']);
    assert.equal(res.status, 0, res.stderr);

    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');
    assert.match(progress, /Hardcore Mode \(100% Student Code, 0% AI Code\)/);
  });

  test('accepts the documented init subcommand', () => {
    const res = runScript(INIT_SCRIPT, ['init', '--track', 'redis']);
    assert.equal(res.status, 0, res.stderr);
    assert.match(res.stdout, /Current milestone:.*TCP Server & PING \/ ECHO/);
    assert.match(res.stdout, /Your first action:/);
    assert.match(res.stdout, /Level 1 analogy/);
  });

  test('refuses to overwrite existing PROGRESS.md without --force', () => {
    const first = runScript(INIT_SCRIPT, ['--track', 'redis']);
    assert.equal(first.status, 0);

    // Second run without --force must fail
    const second = runScript(INIT_SCRIPT, ['--track', 'git']);
    assert.equal(second.status, 1);
    assert.match(second.stderr, /Existing PROGRESS\.md found/);
    assert.match(second.stderr, /Refusing to overwrite/);

    // Check that redis track is still present, not clobbered
    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');
    assert.match(progress, /Track: redis/i);
  });

  test('overwrites existing PROGRESS.md when --force is provided', () => {
    runScript(INIT_SCRIPT, ['--track', 'redis']);

    const overwrite = runScript(INIT_SCRIPT, ['--track', 'git', '--force']);
    assert.equal(overwrite.status, 0, overwrite.stderr);

    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');
    assert.match(progress, /Track: git/i);
  });

  test('preserves existing .agents/rules/scaffold-guardrails.md unless --force is provided', () => {
    const rulesDir = path.join(tempDir, '.agents/rules');
    fs.mkdirSync(rulesDir, { recursive: true });
    const ruleFile = path.join(rulesDir, 'scaffold-guardrails.md');
    fs.writeFileSync(ruleFile, '# Custom User Guardrail', 'utf8');

    // Run init without force
    const res = runScript(INIT_SCRIPT, ['--track', 'redis']);
    assert.equal(res.status, 0);

    const content = fs.readFileSync(ruleFile, 'utf8');
    assert.equal(content, '# Custom User Guardrail', 'Custom rule must be preserved');

    // Run init with force
    const forceRes = runScript(INIT_SCRIPT, ['--track', 'redis', '--force']);
    assert.equal(forceRes.status, 0);

    const updatedContent = fs.readFileSync(ruleFile, 'utf8');
    assert.notEqual(updatedContent, '# Custom User Guardrail', 'Rule should be overwritten with --force');
    assert.match(updatedContent, /Scaffold Guardrails/);
  });

  test('updates CLAUDE.md idempotently if present', () => {
    const claudePath = path.join(tempDir, 'CLAUDE.md');
    fs.writeFileSync(claudePath, '# My Claude Project\n', 'utf8');

    // First init
    runScript(INIT_SCRIPT, ['--track', 'redis']);
    const afterFirst = fs.readFileSync(claudePath, 'utf8');
    assert.match(afterFirst, /Scaffold Guardrails Active/);

    // Count occurrences
    const countMatches = (str, sub) => (str.match(new RegExp(sub, 'g')) || []).length;
    assert.equal(countMatches(afterFirst, 'Scaffold Guardrails Active'), 1);

    // Second init with --force
    runScript(INIT_SCRIPT, ['--track', 'redis', '--force']);
    const afterSecond = fs.readFileSync(claudePath, 'utf8');
    assert.equal(countMatches(afterSecond, 'Scaffold Guardrails Active'), 1, 'Notice must remain idempotent');
  });

  test('rejects unknown track with exit code 1 and lists valid tracks', () => {
    const res = runScript(INIT_SCRIPT, ['--track', 'blockchain-quantum']);
    assert.equal(res.status, 1);
    assert.match(res.stderr, /Unknown track/);
    assert.match(res.stderr, /Available curated tracks: redis, git, http, sqlite, docker/);
  });

  test('rejects malformed arguments', () => {
    const noTrackVal = runScript(INIT_SCRIPT, ['--track']);
    assert.equal(noTrackVal.status, 1);

    const noIdeaVal = runScript(INIT_SCRIPT, ['--idea']);
    assert.equal(noIdeaVal.status, 1);

    const emptyIdea = runScript(INIT_SCRIPT, ['--idea', '   ']);
    assert.equal(emptyIdea.status, 1);

    const badFlag = runScript(INIT_SCRIPT, ['--unrecognized-flag']);
    assert.equal(badFlag.status, 1);
  });

  test('rejects running without --idea or --track with clear usage guidance', () => {
    const res = runScript(INIT_SCRIPT, []);
    assert.equal(res.status, 1);
    assert.match(res.stderr, /Please specify what you want to build or learn/);
    assert.match(res.stderr, /npx scaffold init --idea/);
    assert.match(res.stderr, /npx scaffold init --track/);
  });
});

describe('verify-gate.mjs', () => {
  test('fails cleanly if PROGRESS.md is missing', () => {
    const res = runScript(VERIFY_SCRIPT, ['--milestone', '1']);
    assert.equal(res.status, 1);
    assert.match(res.stderr, /No PROGRESS\.md found/);
  });

  test('rejects skipped milestones and enforces strictly sequential verification', () => {
    runScript(INIT_SCRIPT, ['--track', 'redis']);

    // Attempting to skip Milestone 1 and verify Milestone 2
    const skip2 = runScript(VERIFY_SCRIPT, ['--milestone', '2']);
    assert.equal(skip2.status, 1);
    assert.match(skip2.stderr, /Cannot verify Milestone 2/);
    assert.match(skip2.stderr, /Milestone 1.*must be completed first/);
    assert.match(skip2.stderr, /strictly sequential/);

    // Attempting to verify Milestone 5
    const skip5 = runScript(VERIFY_SCRIPT, ['--milestone', '5']);
    assert.equal(skip5.status, 1);
    assert.match(skip5.stderr, /Cannot verify Milestone 5/);
    assert.match(skip5.stderr, /Milestone 1.*must be completed first/);
  });

  test('verifies milestone 1 sequentially and advances state correctly', () => {
    runScript(INIT_SCRIPT, ['--track', 'redis']);

    const res = runScript(VERIFY_SCRIPT, [
      '--milestone', '1',
      '--aha', 'Length-prefixes prevent buffer split over-reads.',
    ]);
    assert.equal(res.status, 0, res.stderr);
    assert.match(res.stdout, /MILESTONE 1 RECORDED/);
    assert.match(res.stdout, /does not inspect the diff or evaluate the learner/);
    assert.doesNotMatch(res.stdout, /VERIFIED & DEFENDED/);

    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');

    // Milestone 1 must be checked off and verified
    assert.match(progress, /-\s*\[x\]\s*\*\*Milestone 1\*\*:\s*.*✅\s*\*\(Verified\)\*/);

    // Milestone 2 must be the ONLY active milestone
    assert.match(progress, /-\s*\[ \]\s*\*\*Milestone 2\*\*:\s*▶\s*\*\*\[ACTIVE\]\*\*/);
    assert.doesNotMatch(progress, /-\s*\[ \]\s*\*\*Milestone 3\*\*:\s*▶/);

    // Progress percentage updated (1/5 = 20%)
    assert.match(progress, /\*\*20%\*\*\s*\(1\/5 completed\)/);

    // Mental Model Matrix row updated to Mastered
    assert.match(progress, /\|\s*M1\s*\|.*\|\s*🟢 Mastered\s*\|/);

    // Aha moments journal logged
    assert.match(progress, /Length-prefixes prevent buffer split over-reads\./);
  });

  test('supports --guided flag, marking Mental Model Matrix as Guided', () => {
    runScript(INIT_SCRIPT, ['--track', 'redis']);

    const res = runScript(VERIFY_SCRIPT, ['--milestone', '1', '--guided']);
    assert.equal(res.status, 0, res.stderr);

    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');
    assert.match(progress, /\|\s*M1\s*\|.*\|\s*🟡 Guided\s*\|/);
  });

  test('verifies idempotently when re-running already verified milestone', () => {
    runScript(INIT_SCRIPT, ['--track', 'redis']);
    runScript(VERIFY_SCRIPT, ['--milestone', '1', '--aha', 'First insight']);

    const contentBefore = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');

    // Re-verify milestone 1
    const rerun = runScript(VERIFY_SCRIPT, ['--milestone', '1']);
    assert.equal(rerun.status, 0, rerun.stderr);
    assert.match(rerun.stdout, /already verified.*Idempotent rerun/);

    const contentAfter = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');

    // Ensure no duplicate checkmarks or duplicated lines
    assert.doesNotMatch(contentAfter, /✅\s*\*\(Verified\)\*\s*✅/);

    // Count occurrences of Milestone 1 check
    const matches = contentAfter.match(/-\s*\[x\]\s*\*\*Milestone 1\*\*/g);
    assert.equal(matches ? matches.length : 0, 1);
  });

  test('advances through all milestones sequentially and generates completion badge', () => {
    runScript(INIT_SCRIPT, ['--track', 'redis']);

    // Complete all 5 milestones
    for (let m = 1; m <= 5; m++) {
      const res = runScript(VERIFY_SCRIPT, ['--milestone', String(m), '--aha', `Insight ${m}`]);
      assert.equal(res.status, 0, `Milestone ${m} failed: ${res.stderr}`);
    }

    const progress = fs.readFileSync(path.join(tempDir, 'PROGRESS.md'), 'utf8');

    // All milestones checked
    for (let m = 1; m <= 5; m++) {
      assert.match(progress, new RegExp(`-\\s*\\[x\\]\\s*\\*\\*Milestone ${m}\\*\\*`));
    }

    // 100% completed
    assert.match(progress, /\*\*100%\*\*\s*\(5\/5 completed\)/);

    // Completion badge present
    assert.match(progress, /### 🏆 Project Completion & Mastery Badge/);
    assert.match(progress, /Built with Scaffold\.ai/);

    // Running verify again once all completed is idempotent
    const postComplete = runScript(VERIFY_SCRIPT);
    assert.equal(postComplete.status, 0);
    assert.match(postComplete.stdout, /All milestones.*already completed/);

    // Badge should not be duplicated
    const badgeMatches = progress.match(/### 🏆 Project Completion & Mastery Badge/g);
    assert.equal(badgeMatches ? badgeMatches.length : 0, 1);
  });

  test('rejects non-numeric, negative, or out-of-range milestone numbers', () => {
    runScript(INIT_SCRIPT, ['--track', 'redis']);

    const nonNumeric = runScript(VERIFY_SCRIPT, ['--milestone', 'abc']);
    assert.equal(nonNumeric.status, 1);

    const negative = runScript(VERIFY_SCRIPT, ['--milestone', '-1']);
    assert.equal(negative.status, 1);

    const outOfRange = runScript(VERIFY_SCRIPT, ['--milestone', '99']);
    assert.equal(outOfRange.status, 1);
    assert.match(outOfRange.stderr, /does not exist in PROGRESS\.md/);

    const missingVal = runScript(VERIFY_SCRIPT, ['--milestone']);
    assert.equal(missingVal.status, 1);

    const missingAha = runScript(VERIFY_SCRIPT, ['--aha']);
    assert.equal(missingAha.status, 1);

    const badArg = runScript(VERIFY_SCRIPT, ['--unknown-arg']);
    assert.equal(badArg.status, 1);
  });
});
