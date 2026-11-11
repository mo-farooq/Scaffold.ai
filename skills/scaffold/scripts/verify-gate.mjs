#!/usr/bin/env node
/**
 * Scaffold Reflection Gate Recorder Script
 * Records an agent-approved milestone gate in PROGRESS.md strictly sequentially,
 * updates the Mental Model Matrix, and logs Aha Moments idempotently.
 *
 * Usage:
 *   node skills/scaffold/scripts/verify-gate.mjs [--milestone <num>] [--aha "<summary>"] [--guided]
 */

import fs from 'node:fs';
import path from 'node:path';

// Terminal colors
const cyan = (s) => `\x1b[36m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const red = (s) => `\x1b[31m${s}\x1b[0m`;
const bold = (s) => `\x1b[1m${s}\x1b[0m`;

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    guided: false,
    aha: '',
    milestone: null,
    rawMilestone: null,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--milestone') {
      if (i + 1 >= args.length) {
        console.error(red('Error: --milestone requires a number argument.'));
        process.exit(1);
      }
      options.rawMilestone = args[++i];
      const parsed = parseInt(options.rawMilestone, 10);
      if (isNaN(parsed) || String(parsed) !== options.rawMilestone.trim() || parsed <= 0) {
        console.error(red(`Error: Invalid milestone "${options.rawMilestone}". Must be a positive integer.`));
        process.exit(1);
      }
      options.milestone = parsed;
    } else if (arg === '--aha') {
      if (i + 1 >= args.length) {
        console.error(red('Error: --aha requires a text argument.'));
        process.exit(1);
      }
      options.aha = args[++i];
    } else if (arg === '--guided') {
      options.guided = true;
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
  ${bold(cyan('Scaffold Gate Recorder CLI'))}

Usage:
  node verify-gate.mjs [--milestone <num>] [--aha "<summary>"] [--guided]

Options:
  --milestone <num>  Milestone number to verify (must be the next sequential milestone)
  --aha "<summary>"  Learner's 1-sentence architectural takeaway to log in PROGRESS.md
  --guided           Mark mastery state as Guided (L2/L3 hints used) instead of Mastered
  --help, -h         Show this help message
`);
}

function makeProgressBar(percent) {
  const totalBars = 20;
  const clamped = Math.max(0, Math.min(100, percent));
  const filledBars = Math.round((clamped / 100) * totalBars);
  const emptyBars = totalBars - filledBars;
  return '█'.repeat(filledBars) + '░'.repeat(emptyBars);
}

function cleanTitle(raw) {
  return raw
    .replace(/▶\s*\*\*\[ACTIVE\]\*\*\s*/g, '')
    .replace(/✅\s*\*\([^\)]*\)\*/g, '')
    .trim();
}

function main() {
  const progressPath = path.join(process.cwd(), 'PROGRESS.md');
  if (!fs.existsSync(progressPath)) {
    console.error(red(`Error: No PROGRESS.md found in ${process.cwd()}. Run initialization first!`));
    process.exit(1);
  }

  let content = fs.readFileSync(progressPath, 'utf8');
  const options = parseArgs();

  // Parse lines and extract all milestone entries
  const lines = content.split('\n');
  const milestoneIndices = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const match = line.match(/^-\s*\[([ xX])\]\s*\*\*Milestone (\d+)\*\*:\s*(.*)$/);
    if (match) {
      milestoneIndices.push({
        lineIndex: i,
        checked: match[1].toLowerCase() === 'x',
        number: parseInt(match[2], 10),
        titleRaw: match[3],
        titleClean: cleanTitle(match[3]),
      });
    }
  }

  if (milestoneIndices.length === 0) {
    console.error(red('Error: No milestones found in PROGRESS.md! File may be corrupted.'));
    process.exit(1);
  }

  // Ensure milestones are sorted by milestone number
  milestoneIndices.sort((a, b) => a.number - b.number);

  const firstUnchecked = milestoneIndices.find((m) => !m.checked);
  const totalCount = milestoneIndices.length;

  // Case 1: All milestones are already completed
  if (!firstUnchecked) {
    if (options.milestone && options.milestone <= totalCount) {
      console.log(green(`Milestone ${options.milestone} is already verified and all milestones are complete! (Idempotent rerun)`));
      process.exit(0);
    }
    console.log(green('All milestones in PROGRESS.md are already completed! (Idempotent rerun)'));
    process.exit(0);
  }

  // Case 2: Target milestone resolution and sequential validation
  let targetNum;
  if (options.milestone !== null) {
    targetNum = options.milestone;

    // Check if target milestone exists in the project
    const targetMilestone = milestoneIndices.find((m) => m.number === targetNum);
    if (!targetMilestone) {
      console.error(red(`Error: Milestone ${targetNum} does not exist in PROGRESS.md. Project has ${totalCount} milestones.`));
      process.exit(1);
    }

    // Check if already verified (Idempotent rerun)
    if (targetMilestone.checked) {
      console.log(yellow(`Milestone ${targetNum} ("${targetMilestone.titleClean}") is already verified! (Idempotent rerun)`));
      process.exit(0);
    }

    // Reject skipping: target must be the first unchecked milestone
    if (targetNum !== firstUnchecked.number) {
      console.error(red(
        `Error: Cannot verify Milestone ${targetNum}. Milestone ${firstUnchecked.number} ("${firstUnchecked.titleClean}") must be completed first.\n` +
        `Scaffold enforces strictly sequential milestone progression to guarantee foundational mastery.`
      ));
      process.exit(1);
    }
  } else {
    // Default to the first unchecked milestone
    targetNum = firstUnchecked.number;
  }

  const targetMilestone = milestoneIndices.find((m) => m.number === targetNum);

  // 1. Mark target milestone as checked
  lines[targetMilestone.lineIndex] = `- [x] **Milestone ${targetMilestone.number}**: ${targetMilestone.titleClean} ✅ *(Verified)*`;

  // 2. Determine the next active milestone and ensure only ONE active marker exists across all milestones
  const nextMilestone = milestoneIndices.find((m) => m.number === targetNum + 1);
  let nextStageText;

  for (const m of milestoneIndices) {
    if (m.number === targetNum) {
      continue; // Already updated above
    }
    if (nextMilestone && m.number === nextMilestone.number) {
      lines[m.lineIndex] = `- [ ] **Milestone ${m.number}**: ▶ **[ACTIVE]** ${m.titleClean}`;
    } else if (m.checked) {
      lines[m.lineIndex] = `- [x] **Milestone ${m.number}**: ${m.titleClean} ✅ *(Verified)*`;
    } else {
      lines[m.lineIndex] = `- [ ] **Milestone ${m.number}**: ${m.titleClean}`;
    }
  }

  if (nextMilestone) {
    nextStageText = `Milestone ${nextMilestone.number}: ${nextMilestone.titleClean}`;
  } else {
    nextStageText = '🎉 ALL MILESTONES COMPLETED!';
  }

  // 3. Update Mental Model Matrix row
  const masteryBadge = options.guided ? '🟡 Guided' : '🟢 Mastered';
  const matrixRegex = new RegExp(`^\\|\\s*M${targetNum}\\s*\\|([^|]+)\\|([^|]+)\\|([^|]+)\\|`);

  for (let i = 0; i < lines.length; i++) {
    if (matrixRegex.test(lines[i])) {
      lines[i] = `| M${targetNum} | ${targetMilestone.titleClean} | ${masteryBadge} | Defended in 4-Axis Gate |`;
      break;
    }
  }

  // 4. Update Aha Moments Journal idempotently
  const ahaText = options.aha.trim() ||
    'Successfully defended design across 4 engineering axes (Correctness, Edge Cases, Complexity, Security).';

  const ahaPlaceholder = '*Milestone reflections and key takeaways will be recorded here upon completing each gate.*';
  let updatedContent = lines.join('\n');

  const ahaHeader = '## 💡 Aha Moments Journal';
  const milestoneAhaPrefix = `* **Milestone ${targetNum} (`;

  if (updatedContent.includes(ahaHeader)) {
    if (updatedContent.includes(ahaPlaceholder)) {
      updatedContent = updatedContent.replace(
        ahaPlaceholder,
        `* **Milestone ${targetNum} (${targetMilestone.titleClean})**: "${ahaText}"`
      );
    } else if (!updatedContent.includes(milestoneAhaPrefix)) {
      // Append entry right under Aha Moments header
      updatedContent = updatedContent.replace(
        new RegExp(`${ahaHeader}\\n*`),
        `${ahaHeader}\n\n* **Milestone ${targetNum} (${targetMilestone.titleClean})**: "${ahaText}"\n`
      );
    }
  }

  // 5. Update progress counts and dashboard bar
  const completedCount = milestoneIndices.filter((m) => m.checked || m.number === targetNum).length;
  const progressPercent = Math.round((completedCount / totalCount) * 100);
  const progressBar = makeProgressBar(progressPercent);

  updatedContent = updatedContent.replace(
    /\*\*Current Stage\*\*\s*\|\s*\*\*([^*]+)\*\*/,
    `**Current Stage** | **${nextStageText}**`
  );
  updatedContent = updatedContent.replace(
    /\*\*Progress\*\*\s*\|\s*`[^`]+`\s*\*\*\d+%\*\*\s*\(\d+\/\d+ completed\)/,
    `**Progress** | \`${progressBar}\` **${progressPercent}%** (${completedCount}/${totalCount} completed)`
  );

  // 6. Append Completion Badge only once when 100% completed
  const badgeTitle = '### 🏆 Project Completion & Mastery Badge';
  if (progressPercent === 100 && !updatedContent.includes(badgeTitle)) {
    const badgeMarkdown = `
---

${badgeTitle}

Congratulations on completing this project through the **Scaffold.ai Socratic Learning Mode**!  
You built every line of core logic yourself while mastering the underlying architectural trade-offs.

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
${bold(green(`  🎉 MILESTONE ${targetNum} RECORDED!`))}
${green('========================================================================')}

${bold('Progress:')} [${progressBar}] ${bold(cyan(`${progressPercent}%`))} (${completedCount}/${totalCount})
${bold('Mastery State:')} ${masteryBadge}
${options.aha ? `${bold('Aha Moment:')}   "${yellow(options.aha)}"\n` : ''}
${nextMilestone ? `${bold('Next Stage:')}   ${yellow(`Milestone ${nextMilestone.number}: ${nextMilestone.titleClean}`)}` : `${bold('Project State:')} ${green('ALL MILESTONES RECORDED! 🏆')}`}

${bold('Review note:')} This command records the agent-approved reflection gate; it does not inspect the diff or evaluate the learner.

${bold('👉 Check PROGRESS.md in your editor split for updated status.')}
`);
}

main();
