## Description:

Maintains the hekouwang light and dark Typora themes and guides agents through token-driven CSS generation, sampled color matching, font fallback verification, installation, troubleshooting, and Typora theme publishing.

This skill is ready for commercial/non-commercial use.

## Publisher:

[huiyonghkw](https://clawhub.ai/user/huiyonghkw)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and designers use this skill to maintain or adapt Typora themes, especially Chinese long-form light and dark themes, by editing token sources, generating CSS, validating fonts and colors, installing locally, and preparing theme.typora.io submissions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Local installation or publishing commands may run external repository scripts or GitHub CLI operations.

Mitigation: Review install.sh and any GitHub CLI commands before execution, and run them only in a trusted local workspace.

Risk: Theme edits can silently appear ineffective in Typora because modified CSS and fonts may not reload or may fall back without errors.

Mitigation: Follow the documented build, install, full Typora restart, color verification, and font fallback probe steps before treating changes as complete.

## Reference(s):

- [Skill definition](artifact/SKILL.md)
- [tokens.json adjustment guide](artifact/references/tokens.md)
- [Typora theme specification and selector map](artifact/references/typora-spec.md)
- [Font strategy and licensing boundaries](artifact/references/fonts.md)
- [Theme workflow](artifact/references/workflow.md)
- [Project homepage from ClawHub metadata](https://github.com/huiyonghkw/hekouwang-typora-theme)
- [Typora custom theme documentation](https://theme.typora.io/doc/Write-Custom-Theme/)

## Skill Output:

**Output Type(s):** [Guidance, Markdown, Code, Shell commands, Configuration]

**Output Format:** [Markdown guidance with inline shell commands, CSS/token editing instructions, and publishing steps]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces agent guidance for local theme files and Typora workflows; does not produce autonomous network actions.]

## Skill Version(s):

1.3.0 (source: server release evidence and frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
