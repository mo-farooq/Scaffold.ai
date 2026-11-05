#!/usr/bin/env node
/**
 * Scaffold Initialization Helper Script
 * Sets up PROGRESS.md and workspace state for Antigravity & skills.sh
 *
 * Usage:
 *   node skills/scaffold/scripts/init-scaffold.mjs --track redis
 *   node skills/scaffold/scripts/init-scaffold.mjs --idea "Build a rate-limited API in Node.js"
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '../../..');

// Terminal colors
const cyan = (s) => `\x1b[36m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const bold = (s) => `\x1b[1m${s}\x1b[0m`;

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--track' && args[i + 1]) {
      options.track = args[++i].toLowerCase();
    } else if (args[i] === '--idea' && args[i + 1]) {
      options.idea = args[++i];
    } else if (args[i] === '--help' || args[i] === '-h') {
      options.help = true;
    }
  }
  return options;
}

function showHelp() {
  console.log(`
${bold(cyan('🏗️ Scaffold Initialization CLI'))}

Usage:
  npx scaffold init --track <track-name>
  npx scaffold init --idea "<project idea>"

Available Curated Tracks:
  • ${bold('redis')}   - Build a Redis Clone from Scratch (RESP & Key-Value Engine)
  • ${bold('git')}     - Build Git from Scratch (Content-Addressable Object Store & DAG)
  • ${bold('http')}    - Build an HTTP/1.1 Server from Raw Sockets (RFC 7230)
  • ${bold('sqlite')}  - Build a Mini SQLite Clone (B+ Trees & Paged Disk Storage)
  • ${bold('docker')}  - Build a Container Runtime (Linux Namespaces & cgroups)
`);
}

function loadTrackMilestones(trackName) {
  const trackFile = path.join(REPO_ROOT, 'tracks', `${trackName}-from-scratch.md`);
  if (!fs.existsSync(trackFile)) {
    throw new Error(`Track "${trackName}" not found at ${trackFile}`);
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

  return { title, milestones };
}

function generateDefaultMilestones(idea) {
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

function main() {
  const options = parseArgs();
  if (options.help) {
    showHelp();
    process.exit(0);
  }

  let projectData;
  let trackOrIdea;

  if (options.track) {
    trackOrIdea = `Track: ${options.track}`;
    projectData = loadTrackMilestones(options.track);
  } else if (options.idea) {
    trackOrIdea = options.idea;
    projectData = generateDefaultMilestones(options.idea);
  } else {
    // Default to redis track if nothing specified
    console.log(yellow('No track or idea specified. Defaulting to curated track: redis\n'));
    trackOrIdea = 'Track: redis';
    projectData = loadTrackMilestones('redis');
  }

  const templatePath = path.join(REPO_ROOT, 'skills/scaffold/assets/PROGRESS.template.md');
  if (!fs.existsSync(templatePath)) {
    console.error(`Template not found at: ${templatePath}`);
    process.exit(1);
  }

  let template = fs.readFileSync(templatePath, 'utf8');

  // Format milestones markdown checklist
  const milestonesList = projectData.milestones
    .map((m, idx) => {
      const activeMark = idx === 0 ? '▶ **[ACTIVE]** ' : '';
      return `- [ ] **Milestone ${m.number}**: ${activeMark}${m.title}`;
    })
    .join('\n');

  const initialDecisions = `| 1 | *In Progress* | - | Initializing ${projectData.milestones[0].title} |`;

  // Fill in placeholders
  const filledProgress = template
    .replace(/\{\{PROJECT_TITLE\}\}/g, projectData.title)
    .replace(/\{\{TRACK_OR_IDEA\}\}/g, trackOrIdea)
    .replace(/\{\{CURRENT_MILESTONE_NUM\}\}/g, '1')
    .replace(/\{\{CURRENT_MILESTONE_TITLE\}\}/g, projectData.milestones[0].title)
    .replace(/\{\{PROGRESS_BAR\}\}/g, '░░░░░░░░░░░░░░░░░░░░')
    .replace(/\{\{PROGRESS_PERCENT\}\}/g, '0')
    .replace(/\{\{COMPLETED_COUNT\}\}/g, '0')
    .replace(/\{\{TOTAL_COUNT\}\}/g, String(projectData.milestones.length))
    .replace(/\{\{MASTERY_SCORE\}\}/g, '100')
    .replace(/\{\{MILESTONES_LIST\}\}/g, milestonesList)
    .replace(/\{\{DECISIONS_LOG\}\}/g, initialDecisions);

  // Write PROGRESS.md to current working directory
  const targetPath = path.join(process.cwd(), 'PROGRESS.md');
  fs.writeFileSync(targetPath, filledProgress, 'utf8');

  console.log(`
${green('✅ Scaffold initialized successfully!')}
File created: ${bold(cyan(targetPath))}

${bold('👉 NEXT STEPS:')}
1. Open ${bold('PROGRESS.md')} in your editor's right split (${cyan('Cmd+Shift+V')} or ${cyan('Ctrl+Shift+V')}).
2. Ask your agent: ${yellow('"What is our architectural goal for Milestone 1?"')}
3. Build with Socratic guidance! When finished, run ${cyan('/scaffold verify')}.
`);
}

main();
