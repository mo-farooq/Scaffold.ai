#!/usr/bin/env node
/**
 * Scaffold Initialization Helper Script
 * Sets up PROGRESS.md and workspace guardrails safely for Antigravity & skills.sh
 *
 * Usage:
 *   node skills/scaffold/scripts/init-scaffold.mjs --track redis [--force] [--hardcore]
 *   node skills/scaffold/scripts/init-scaffold.mjs --idea "Build a rate-limited API in Node.js" [--force]
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, '..');
const ASSETS_DIR = path.join(SKILL_ROOT, 'assets');
const TRACKS_DIR = path.join(ASSETS_DIR, 'tracks');
const RULES_SOURCE = path.join(ASSETS_DIR, 'rules/scaffold-guardrails.md');
const TEMPLATE_PATH = path.join(ASSETS_DIR, 'PROGRESS.template.md');

const VALID_TRACKS = ['redis', 'git', 'http', 'sqlite', 'docker'];
const TRACK_FILE_MAP = {
  redis: 'redis-from-scratch.md',
  git: 'git-from-scratch.md',
  http: 'http-server-from-scratch.md',
  sqlite: 'sqlite-from-scratch.md',
  docker: 'docker-from-scratch.md',
};

// Terminal colors
const cyan = (s) => `\x1b[36m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const red = (s) => `\x1b[31m${s}\x1b[0m`;
const bold = (s) => `\x1b[1m${s}\x1b[0m`;

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    hardcore: false,
    force: false,
    track: null,
    idea: null,
    milestones: null,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (i === 0 && arg === 'init') {
      continue;
    }
    if (arg === '--track') {
      if (i + 1 >= args.length) {
        console.error(red('Error: --track requires a track name.'));
        process.exit(1);
      }
      options.track = args[++i].toLowerCase();
    } else if (arg === '--idea') {
      if (i + 1 >= args.length) {
        console.error(red('Error: --idea requires a project description text.'));
        process.exit(1);
      }
      const val = args[++i].trim();
      if (!val) {
        console.error(red('Error: Project idea description cannot be empty.'));
        process.exit(1);
      }
      options.idea = val;
    } else if (arg === '--milestones') {
      if (i + 1 >= args.length) {
        console.error(red('Error: --milestones requires a delimited list (e.g. "M1|M2|M3").'));
        process.exit(1);
      }
      const raw = args[++i].trim();
      const delimiter = raw.includes('|') ? '|' : (raw.includes(',') ? ',' : ';');
      options.milestones = raw.split(delimiter).map(s => s.trim()).filter(Boolean);
    } else if (arg === '--hardcore') {
      options.hardcore = true;
    } else if (arg === '--force' || arg === '-f') {
      options.force = true;
    } else if (arg === '--help' || arg === '-h') {
      showHelp();
      process.exit(0);
    } else {
      console.error(red(`Error: Unrecognized option "${arg}". Run with --help for usage.`));
      process.exit(1);
    }
  }

  return options;
}

function showHelp() {
  console.log(`
${bold(cyan('🏗️ Scaffold Initialization CLI — Learn to Code with AI'))}

Usage:
  npx scaffold init --idea "<project idea>" [--milestones "<m1|m2|...>"] [--hardcore]
  npx scaffold init --track <track-name> [--hardcore]

Options:
  --idea "<text>"         Decompose your custom learning goal or project into milestones (Recommended)
  --milestones "<list>"   Optional pipe-separated milestone titles for custom ideas (e.g. "M1|M2|M3")
  --track <name>          Start a curated systems playground (redis, git, http, sqlite, docker)
  --hardcore              Hardcore Mode: You write 100% of the code; agent provides hints & review
  --force, -f             Overwrite existing PROGRESS.md and update workspace guardrails
  --help, -h              Show this help message

Curated Practice Playgrounds:
  • ${bold('redis')}   - Build a Redis Clone from Scratch (RESP & Key-Value Engine)
  • ${bold('git')}     - Build Git from Scratch (Content-Addressable Object Store & DAG)
  • ${bold('http')}    - Build an HTTP/1.1 Server from Raw Sockets (RFC 7230)
  • ${bold('sqlite')}  - Build a Mini SQLite Clone (B+ Trees & Paged Disk Storage)
  • ${bold('docker')}  - Build a Container Runtime (Linux Namespaces & cgroups)
`);
}

function loadTrackMilestones(trackName) {
  if (!VALID_TRACKS.includes(trackName)) {
    console.error(red(
      `Error: Unknown track "${trackName}".\n` +
      `Available curated tracks: ${VALID_TRACKS.join(', ')}`
    ));
    process.exit(1);
  }

  const fileName = TRACK_FILE_MAP[trackName] || `${trackName}-from-scratch.md`;

  // Try self-contained assets/tracks first, then fallback to cwd/tracks
  let trackFile = path.join(TRACKS_DIR, fileName);
  if (!fs.existsSync(trackFile)) {
    trackFile = path.join(process.cwd(), 'tracks', fileName);
  }
  if (!fs.existsSync(trackFile)) {
    console.error(red(`Error: Track file for "${trackName}" not found at ${trackFile}`));
    process.exit(1);
  }

  const content = fs.readFileSync(trackFile, 'utf8');
  const titleMatch = content.match(/^# Track:\s*(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : `${trackName.toUpperCase()} from Scratch`;

  // Parse milestones from markdown headers
  const milestoneRegex = /### Milestone (\d+):\s*(.+)/g;
  const milestones = [];
  let match;
  while ((match = milestoneRegex.exec(content)) !== null) {
    milestones.push({
      number: parseInt(match[1], 10),
      title: match[2].trim(),
    });
  }

  if (milestones.length === 0) {
    console.error(red(`Error: No milestones found in track file: ${trackFile}`));
    process.exit(1);
  }

  return { title, milestones };
}

function generateMilestonesFromIdea(idea, customMilestones) {
  if (customMilestones && customMilestones.length > 0) {
    return {
      title: idea,
      milestones: customMilestones.map((title, idx) => ({
        number: idx + 1,
        title: title.trim(),
      })),
    };
  }
  return {
    title: idea,
    milestones: [
      { number: 1, title: 'Core Architecture, Types & Data Models' },
      { number: 2, title: 'Core Processing Engine & Business Logic' },
      { number: 3, title: 'I/O Interface, Parsing & Error Handling' },
      { number: 4, title: 'Persistence, Validation & Integration Tests' },
    ],
  };
}

function setupWorkspaceGuardrails(options) {
  const warnings = [];
  try {
    const targetAgentsRulesDir = path.join(process.cwd(), '.agents/rules');
    if (!fs.existsSync(targetAgentsRulesDir)) {
      fs.mkdirSync(targetAgentsRulesDir, { recursive: true });
    }
    const targetRulePath = path.join(targetAgentsRulesDir, 'scaffold-guardrails.md');

    if (fs.existsSync(targetRulePath) && !options.force) {
      console.log(yellow('Preserving existing .agents/rules/scaffold-guardrails.md (use --force to overwrite).'));
    } else if (fs.existsSync(RULES_SOURCE)) {
      fs.copyFileSync(RULES_SOURCE, targetRulePath);
    }

    // Claude Code compatibility: check CLAUDE.md if present
    const claudeMdPath = path.join(process.cwd(), 'CLAUDE.md');
    if (fs.existsSync(claudeMdPath)) {
      const claudeContent = fs.readFileSync(claudeMdPath, 'utf8');
      const marker = '<!-- Scaffold Guardrails Active -->';
      if (!claudeContent.includes(marker)) {
        const notice = `\n\n${marker}\n> [!IMPORTANT]\n> When PROGRESS.md is present, enforce Scaffold Socratic guardrails (.agents/rules/scaffold-guardrails.md): never fill in TODO(scaffold) stubs for the learner. Provide 3-level progressive hints and enforce the 4-axis reflection gate.\n`;
        fs.appendFileSync(claudeMdPath, notice, 'utf8');
      }
    }
  } catch (err) {
    warnings.push(`Workspace guardrail setup was incomplete: ${err.message}`);
  }
  return warnings;
}

function main() {
  const options = parseArgs();

  // Safety check: Refuse to overwrite existing PROGRESS.md without --force
  const targetPath = path.join(process.cwd(), 'PROGRESS.md');
  if (fs.existsSync(targetPath) && !options.force) {
    console.error(red(
      `Error: Existing PROGRESS.md found in ${process.cwd()}.\n` +
      `Refusing to overwrite to prevent losing existing learning progress.\n` +
      `Use --force if you intentionally wish to reset this workspace.`
    ));
    process.exit(1);
  }

  let projectData;
  let trackOrIdea;

  if (options.track) {
    trackOrIdea = `Track: ${options.track}`;
    projectData = loadTrackMilestones(options.track);
  } else if (options.idea) {
    trackOrIdea = options.idea;
    projectData = generateMilestonesFromIdea(options.idea, options.milestones);
  } else {
    console.log(yellow(
      'Tip: You can start any custom project with: npx scaffold init --idea "<what you want to learn>"\n' +
      'Defaulting to curated playground: redis\n'
    ));
    trackOrIdea = 'Track: redis';
    projectData = loadTrackMilestones('redis');
  }

  if (!fs.existsSync(TEMPLATE_PATH)) {
    console.error(red(`Error: Template not found at: ${TEMPLATE_PATH}`));
    process.exit(1);
  }

  let template = fs.readFileSync(TEMPLATE_PATH, 'utf8');

  // Format milestones markdown checklist
  const milestonesList = projectData.milestones
    .map((m, idx) => {
      const activeMark = idx === 0 ? '▶ **[ACTIVE]** ' : '';
      return `- [ ] **Milestone ${m.number}**: ${activeMark}${m.title}`;
    })
    .join('\n');

  // Format Concept Mastery Matrix
  const masteryMatrix = projectData.milestones
    .map((m) => `| M${m.number} | ${m.title} | 🔴 Not reviewed | Pending 4-Axis Diff Review |`)
    .join('\n');

  const executionMode = options.hardcore
    ? 'Hardcore Mode (100% Student Code, 0% AI Code)'
    : 'Mentor Mode (AI Boilerplate Glue + TODO(scaffold) Stubs)';

  const firstMilestone = projectData.milestones[0];
  const currentMilestoneGoal = `Build the first observable outcome of ${firstMilestone.title}.`;
  const nextAction = options.hardcore
    ? `Create the first source file needed for ${firstMilestone.title}.`
    : 'Ask your agent for the architectural briefing, then locate the first TODO(scaffold) stub.';
  const learnerOwnership = options.hardcore
    ? 'All source files, boilerplate, and core logic.'
    : 'Core algorithmic logic inside TODO(scaffold) blocks and the design decisions behind it.';
  const agentOwnership = options.hardcore
    ? 'Architecture, questions, progressive hints, and reflection review; no source-code files.'
    : 'Environment setup, configuration, test harnesses, entry-point wiring, and explicit stubs.';

  const initialDecisions = `| 1 | *In Progress* | - | Initializing ${firstMilestone.title} |`;
  const initialAhaLog = `*Milestone reflections and key takeaways will be recorded here upon completing each gate.*`;

  // Fill in placeholders
  const filledProgress = template
    .replace(/\{\{PROJECT_TITLE\}\}/g, projectData.title)
    .replace(/\{\{TRACK_OR_IDEA\}\}/g, trackOrIdea)
    .replace(/\{\{EXECUTION_MODE\}\}/g, executionMode)
    .replace(/\{\{CURRENT_MILESTONE_NUM\}\}/g, '1')
    .replace(/\{\{CURRENT_MILESTONE_TITLE\}\}/g, firstMilestone.title)
    .replace(/\{\{CURRENT_MILESTONE_GOAL\}\}/g, currentMilestoneGoal)
    .replace(/\{\{NEXT_ACTION\}\}/g, nextAction)
    .replace(/\{\{LEARNER_OWNERSHIP\}\}/g, learnerOwnership)
    .replace(/\{\{AGENT_OWNERSHIP\}\}/g, agentOwnership)
    .replace(/\{\{PROGRESS_BAR\}\}/g, '░░░░░░░░░░░░░░░░░░░░')
    .replace(/\{\{PROGRESS_PERCENT\}\}/g, '0')
    .replace(/\{\{COMPLETED_COUNT\}\}/g, '0')
    .replace(/\{\{TOTAL_COUNT\}\}/g, String(projectData.milestones.length))
    .replace(/\{\{MASTERY_SCORE\}\}/g, 'Not yet reviewed')
    .replace(/\{\{MASTERY_MATRIX\}\}/g, masteryMatrix)
    .replace(/\{\{MILESTONES_LIST\}\}/g, milestonesList)
    .replace(/\{\{DECISIONS_LOG\}\}/g, initialDecisions)
    .replace(/\{\{AHA_MOMENTS_LOG\}\}/g, initialAhaLog);

  // Write PROGRESS.md to current working directory
  fs.writeFileSync(targetPath, filledProgress, 'utf8');

  // Set up workspace guardrails in .agents/rules/
  const guardrailWarnings = setupWorkspaceGuardrails(options);

  console.log(`
${green('✅ Scaffold initialized successfully!')}
File created: ${bold(cyan(targetPath))}
Mode:         ${bold(yellow(executionMode))}
${guardrailWarnings.length ? `\n${guardrailWarnings.map((warning) => yellow(`Warning: ${warning}`)).join('\n')}` : ''}

${bold('👉 NEXT STEPS:')}
1. Open ${bold('PROGRESS.md')} in your editor's right split (${cyan('Cmd+Shift+V')} or ${cyan('Ctrl+Shift+V')}).
2. ${yellow('Snooze AI ghost-text')} so inline auto-complete doesn't spoil the learning loop.
3. ${bold('Current milestone:')} ${firstMilestone.title}
4. ${bold('Your first action:')} ${nextAction}
5. ${bold('Need help?')} Ask for a ${yellow('Level 1 analogy and guiding question')}.
6. When finished, ask your agent for the ${cyan('4-axis reflection gate')} before running verification.
`);
}

main();
