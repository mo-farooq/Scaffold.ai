#!/usr/bin/env node
/**
 * Git Worktree Management CLI for Scaffold.ai
 *
 * Provides safe, isolated workspace management in .worktrees/
 *
 * Commands:
 *   node scripts/worktree.mjs list
 *   node scripts/worktree.mjs add <name> [base-branch] [--branch <branch>]
 *   node scripts/worktree.mjs remove <name> [--force]
 */

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');
const WORKTREES_DIR = path.join(REPO_ROOT, '.worktrees');

// Terminal colors
const cyan = (s) => `\x1b[36m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const red = (s) => `\x1b[31m${s}\x1b[0m`;
const bold = (s) => `\x1b[1m${s}\x1b[0m`;
const dim = (s) => `\x1b[2m${s}\x1b[0m`;

function runGit(args, cwd = REPO_ROOT) {
  return spawnSync('git', args, {
    cwd,
    encoding: 'utf8',
  });
}

/**
 * Returns an array of parsed worktree objects
 */
export function getWorktrees(cwd = REPO_ROOT) {
  const res = runGit(['worktree', 'list', '--porcelain'], cwd);
  if (res.status !== 0) {
    throw new Error(`Failed to list worktrees: ${res.stderr || res.stdout}`);
  }

  const raw = res.stdout.trim();
  if (!raw) return [];

  const entries = raw.split(/\n\s*\n/);
  const worktrees = [];

  for (const entry of entries) {
    const lines = entry.split('\n');
    let wtPath = '';
    let head = '';
    let branch = '';
    let isBare = false;
    let isDetached = false;

    for (const line of lines) {
      if (line.startsWith('worktree ')) {
        wtPath = line.substring(9).trim();
      } else if (line.startsWith('HEAD ')) {
        head = line.substring(5).trim();
      } else if (line.startsWith('branch ')) {
        const ref = line.substring(7).trim();
        branch = ref.replace(/^refs\/heads\//, '');
      } else if (line === 'bare') {
        isBare = true;
      } else if (line === 'detached') {
        isDetached = true;
      }
    }

    if (wtPath) {
      let isDirty = false;
      if (fs.existsSync(wtPath)) {
        const stRes = runGit(['status', '--porcelain'], wtPath);
        if (stRes.status === 0 && stRes.stdout.trim().length > 0) {
          isDirty = true;
        }
      }

      worktrees.push({
        path: wtPath,
        head: head.slice(0, 7),
        branch: branch || (isDetached ? '(detached)' : '(bare)'),
        isBare,
        isDetached,
        isDirty,
        isRoot: path.resolve(wtPath) === path.resolve(cwd),
      });
    }
  }

  return worktrees;
}

export function listWorktrees(cwd = REPO_ROOT) {
  const worktrees = getWorktrees(cwd);

  console.log(bold('\n🌿 Active Git Worktrees:\n'));

  if (worktrees.length === 0) {
    console.log(dim('  No worktrees found.'));
    return;
  }

  for (const wt of worktrees) {
    const relPath = path.relative(cwd, wt.path) || '.';
    const branchTag = wt.branch ? cyan(wt.branch) : dim('(no branch)');
    const commitTag = yellow(wt.head);
    const statusTag = wt.isDirty ? red('● dirty') : green('✔ clean');
    const rootTag = wt.isRoot ? dim(' [main checkout]') : '';

    console.log(`  • ${bold(relPath)}`);
    console.log(`    Branch: ${branchTag}  Commit: ${commitTag}  Status: ${statusTag}${rootTag}`);
    console.log(`    Path: ${dim(wt.path)}\n`);
  }
}

export function addWorktree(name, options = {}, cwd = REPO_ROOT) {
  if (!name || typeof name !== 'string' || !name.trim()) {
    console.error(red('Error: Worktree name is required.'));
    console.log('Usage: npm run worktree:add <name> [base-branch] [--branch <branch>]');
    process.exit(1);
  }

  const cleanName = name.trim();
  // Safe folder name in .worktrees (strip leading slashes or prefixes like feat/)
  const folderName = cleanName.replace(/^[a-zA-Z0-9_\-]+\//, '').replace(/[^a-zA-Z0-9_\-]/g, '-');
  const targetDir = path.join(cwd, '.worktrees', folderName);

  // Check if directory already exists
  if (fs.existsSync(targetDir)) {
    console.error(red(`Error: Destination directory already exists: ${path.relative(cwd, targetDir)}`));
    process.exit(1);
  }

  // Determine branch name
  let targetBranch = options.branch;
  if (!targetBranch) {
    targetBranch = cleanName.includes('/') ? cleanName : `feat/${cleanName}`;
  }

  const baseBranch = options.base || 'main';

  // Ensure .worktrees directory exists
  const worktreesDir = path.join(cwd, '.worktrees');
  if (!fs.existsSync(worktreesDir)) {
    fs.mkdirSync(worktreesDir, { recursive: true });
  }

  // Check if branch already exists locally
  const branchCheck = runGit(['show-ref', '--verify', `refs/heads/${targetBranch}`], cwd);
  const branchExists = branchCheck.status === 0;

  console.log(cyan(`\n🌿 Creating worktree at: .worktrees/${folderName}`));

  let addArgs;
  if (branchExists) {
    console.log(`   Checking out existing branch: ${yellow(targetBranch)}`);
    addArgs = ['worktree', 'add', targetDir, targetBranch];
  } else {
    // Check if remote branch exists
    const remoteCheck = runGit(['show-ref', '--verify', `refs/remotes/origin/${targetBranch}`], cwd);
    if (remoteCheck.status === 0) {
      console.log(`   Tracking remote branch: ${yellow(targetBranch)}`);
      addArgs = ['worktree', 'add', '--track', '-b', targetBranch, targetDir, `origin/${targetBranch}`];
    } else {
      console.log(`   Creating new branch: ${yellow(targetBranch)} (based on ${baseBranch})`);
      addArgs = ['worktree', 'add', '-b', targetBranch, targetDir, baseBranch];
    }
  }

  const res = runGit(addArgs, cwd);
  if (res.status !== 0) {
    console.error(red(`\nFailed to create worktree: ${res.stderr || res.stdout}`));
    process.exit(1);
  }

  console.log(green('\n✔ Worktree created successfully!'));
  console.log(`  Branch:    ${cyan(targetBranch)}`);
  console.log(`  Directory: ${bold(`.worktrees/${folderName}`)}`);
  console.log(`\nTo switch to your new worktree:\n  ${yellow(`cd .worktrees/${folderName}`)}\n`);
}

export function removeWorktree(name, options = {}, cwd = REPO_ROOT) {
  if (!name || typeof name !== 'string' || !name.trim()) {
    console.error(red('Error: Worktree name or path is required.'));
    console.log('Usage: npm run worktree:remove <name> [--force]');
    process.exit(1);
  }

  const target = name.trim();
  const worktrees = getWorktrees(cwd);

  // Match by folder name, relative path, branch name, or absolute path
  const match = worktrees.find((wt) => {
    if (wt.isRoot) return false;
    const rel = path.relative(cwd, wt.path);
    const base = path.basename(wt.path);
    return rel === target || base === target || wt.branch === target || wt.path === target || rel === `.worktrees/${target}`;
  });

  if (!match) {
    console.error(red(`Error: No active worktree found matching "${target}".`));
    console.log('Run `npm run worktree:list` to see active worktrees.');
    process.exit(1);
  }

  if (match.isDirty && !options.force) {
    console.error(red(`\nError: Worktree at "${path.relative(cwd, match.path)}" contains uncommitted changes.`));
    console.log(yellow('Please commit or stash your changes, or run with --force to remove anyway.'));
    process.exit(1);
  }

  console.log(cyan(`\n🗑 Removing worktree: ${path.relative(cwd, match.path)} [${match.branch}]`));

  const rmArgs = ['worktree', 'remove'];
  if (options.force) {
    rmArgs.push('--force');
  }
  rmArgs.push(match.path);

  const res = runGit(rmArgs, cwd);
  if (res.status !== 0) {
    console.error(red(`Failed to remove worktree: ${res.stderr || res.stdout}`));
    process.exit(1);
  }

  // Prune dead worktree metadata
  runGit(['worktree', 'prune'], cwd);

  console.log(green(`✔ Worktree "${path.basename(match.path)}" removed successfully.\n`));
}

function printHelp() {
  console.log(`
${bold('Scaffold.ai Worktree Manager')}
Isolated workspace development for agents and learners.

${bold('Usage:')}
  node scripts/worktree.mjs <command> [options]

${bold('Commands:')}
  ${cyan('list')}
      List all active git worktrees with status and branch details.
      ${dim('npm run worktree:list')}

  ${cyan('add <name> [base-branch] [--branch <branch>]')}
      Create an isolated worktree in .worktrees/<name> with a dedicated branch.
      ${dim('npm run worktree:add reposition')}
      ${dim('npm run worktree:add auth main --branch feat/oauth2')}

  ${cyan('remove <name> [--force]')}
      Safely remove an active worktree and prune metadata.
      ${dim('npm run worktree:remove reposition')}
      ${dim('npm run worktree:remove reposition --force')}

  ${cyan('help, --help, -h')}
      Show this help documentation.
`);
}

function parseCliArgs() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === 'help' || command === '--help' || command === '-h') {
    printHelp();
    return;
  }

  if (command === 'list') {
    listWorktrees(process.cwd());
    return;
  }

  if (command === 'add') {
    const name = args[1];
    let base = null;
    let branch = null;

    for (let i = 2; i < args.length; i++) {
      if (args[i] === '--branch' || args[i] === '-b') {
        branch = args[++i];
      } else if (args[i] === '--base') {
        base = args[++i];
      } else if (!base && !args[i].startsWith('-')) {
        base = args[i];
      }
    }

    addWorktree(name, { base, branch }, process.cwd());
    return;
  }

  if (command === 'remove') {
    const name = args[1];
    const force = args.includes('--force') || args.includes('-f');
    removeWorktree(name, { force }, process.cwd());
    return;
  }

  console.error(red(`Error: Unknown command "${command}".`));
  printHelp();
  process.exit(1);
}

// Only invoke CLI parser when executed directly
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(__filename)) {
  parseCliArgs();
}
