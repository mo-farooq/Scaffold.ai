#!/usr/bin/env node
/**
 * Scaffold Reflection Gate Verification Script
 * Unlocks the next milestone in PROGRESS.md and generates completion badges.
 *
 * Usage:
 *   node skills/scaffold/scripts/verify-gate.mjs --milestone 1
 */

import fs from 'node:fs';
import path from 'node:path';

// Terminal colors
const cyan = (s) => `\x1b[36m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const bold = (s) => `\x1b[1m${s}\x1b[0m`;

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--milestone' && args[i + 1]) {
      options.milestone = parseInt(args[++i], 10);
    }
  }
  return options;
}

function makeProgressBar(percent) {
  const totalBars = 20;
  const filledBars = Math.round((percent / 100) * totalBars);
  const emptyBars = totalBars - filledBars;
  return '█'.repeat(filledBars) + '░'.repeat(emptyBars);
}

function main() {
  const progressPath = path.join(process.cwd(), 'PROGRESS.md');
  if (!fs.existsSync(progressPath)) {
    console.error(`No PROGRESS.md found in ${process.cwd()}. Run initialization first!`);
    process.exit(1);
  }

  let content = fs.readFileSync(progressPath, 'utf8');
  const options = parseArgs();

  // Find all milestone checkboxes
  // Format: - [ ] **Milestone 1**: [optional active marker] Title
  const milestoneLines = content.split('\n');
  const milestoneIndices = [];

  for (let i = 0; i < milestoneLines.length; i++) {
    const line = milestoneLines[i];
    const match = line.match(/^-\s*\[([ xX])\]\s*\*\*Milestone (\d+)\*\*:\s*(.*)$/);
    if (match) {
      milestoneIndices.push({
        lineIndex: i,
        checked: match[1].toLowerCase() === 'x',
        number: parseInt(match[2], 10),
        titleRaw: match[3],
        titleClean: match[3].replace(/▶\s*\*\*\[ACTIVE\]\*\*\s*/g, '').trim(),
      });
    }
  }

  if (milestoneIndices.length === 0) {
    console.error('No milestones found in PROGRESS.md!');
    process.exit(1);
  }

  // Determine which milestone to verify
  let targetNum = options.milestone;
  if (!targetNum) {
    // Pick the first unchecked milestone
    const firstUnchecked = milestoneIndices.find((m) => !m.checked);
    if (!firstUnchecked) {
      console.log(green('🎉 All milestones are already completed!'));
      process.exit(0);
    }
    targetNum = firstUnchecked.number;
  }

  const targetMilestone = milestoneIndices.find((m) => m.number === targetNum);
  if (!targetMilestone) {
    console.error(`Milestone ${targetNum} not found in PROGRESS.md.`);
    process.exit(1);
  }

  // Check off the target milestone
  milestoneLines[targetMilestone.lineIndex] = `- [x] **Milestone ${targetMilestone.number}**: ${targetMilestone.titleClean} ✅ *(Verified)*`;

  // Determine the next milestone
  const nextMilestone = milestoneIndices.find((m) => m.number === targetNum + 1);
  let nextStageText;
  let nextMilestoneNum;
  let nextMilestoneTitle;

  if (nextMilestone) {
    // Set next milestone as active
    milestoneLines[nextMilestone.lineIndex] = `- [ ] **Milestone ${nextMilestone.number}**: ▶ **[ACTIVE]** ${nextMilestone.titleClean}`;
    nextStageText = `Milestone ${nextMilestone.number}: ${nextMilestone.titleClean}`;
    nextMilestoneNum = String(nextMilestone.number);
    nextMilestoneTitle = nextMilestone.titleClean;
  } else {
    nextStageText = '🎉 ALL MILESTONES COMPLETED!';
    nextMilestoneNum = 'Done';
    nextMilestoneTitle = 'Completed';
  }

  // Count newly completed milestones
  const totalCount = milestoneIndices.length;
  let completedCount = milestoneIndices.filter((m) => m.checked || m.number === targetNum).length;
  const progressPercent = Math.round((completedCount / totalCount) * 100);
  const progressBar = makeProgressBar(progressPercent);

  let updatedContent = milestoneLines.join('\n');

  // Update Dashboard table metrics
  updatedContent = updatedContent.replace(
    /\*\*Current Stage\*\*\s*\|\s*\*\*Milestone [^|]+\*\*/,
    `**Current Stage** | **${nextStageText}**`
  );
  updatedContent = updatedContent.replace(
    /\*\*Progress\*\*\s*\|\s*`[^`]+`\s*\*\*\d+%\*\*\s*\(\d+\/\d+ completed\)/,
    `**Progress** | \`${progressBar}\` **${progressPercent}%** (${completedCount}/${totalCount} completed)`
  );

  // If 100% completed, append the Shareable Mastery Badge
  if (progressPercent === 100 && !updatedContent.includes('### 🏆 Project Completion & Mastery Badge')) {
    const badgeMarkdown = `
---

### 🏆 Project Completion & Mastery Badge

Congratulations on completing this project through the **Scaffold.ai Socratic Learning Mode**!  
You built every line of this system yourself while mastering the underlying architectural trade-offs.

Copy this badge into your project's \`README.md\`:

\`\`\`markdown
[![Built with Scaffold.ai](https://img.shields.io/badge/Socratic%20Engineering-Scaffold.ai-36c?style=for-the-badge&logo=anthropic)](https://github.com/mo-farooq/Scaffold.ai)
\`\`\`

> *"Mastery is built through friction, design choices, and deliberate coding—not passive prompt-dumping."*
`;
    updatedContent += badgeMarkdown;
  }

  fs.writeFileSync(progressPath, updatedContent, 'utf8');

  console.log(`
${green('========================================================================')}
${bold(green(`  🎉 MILESTONE ${targetNum} VERIFIED & UNLOCKED!`))}
${green('========================================================================')}

${bold('Progress:')} [${progressBar}] ${bold(cyan(`${progressPercent}%`))} (${completedCount}/${totalCount})
${nextMilestone ? `${bold('Next Active Stage:')} ${yellow(`Milestone ${nextMilestone.number}: ${nextMilestone.titleClean}`)}` : `${bold('Project Status:')} ${green('COMPLETE! 🏆')}`}

${bold('👉 Check PROGRESS.md in your editor split for updated status.')}
`);
}

main();
