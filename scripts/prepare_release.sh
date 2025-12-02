#!/bin/bash
# Script to prepare v0.9-pre-submission release
# This script helps prepare files for GitHub release

set -e

VERSION="v0.9-pre-submission"
RELEASE_DIR="release_${VERSION}"

echo "Preparing release: ${VERSION}"

# Create release directory
mkdir -p "${RELEASE_DIR}"

# Copy PDFs (assuming they are generated)
if [ -f "ethical_riemann_hypothesis_en.pdf" ]; then
    cp ethical_riemann_hypothesis_en.pdf "${RELEASE_DIR}/"
    echo "✓ Copied English PDF"
else
    echo "⚠ Warning: ethical_riemann_hypothesis_en.pdf not found. Please compile first."
fi

if [ -f "ethical_riemann_hypothesis_zh.pdf" ]; then
    cp ethical_riemann_hypothesis_zh.pdf "${RELEASE_DIR}/"
    echo "✓ Copied Chinese PDF"
else
    echo "⚠ Warning: ethical_riemann_hypothesis_zh.pdf not found. Please compile first."
fi

# Create supplementary material archive
echo "Creating supplementary material archive..."
tar -czf "${RELEASE_DIR}/supplementary_material.tar.gz" \
    docs/EXPERIMENT_REPORTS.md \
    simulation/output/ \
    data/ \
    figures/ \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="*.ipynb_checkpoints"

echo "✓ Created supplementary_material.tar.gz"

# Create release notes
cat > "${RELEASE_DIR}/RELEASE_NOTES.md" << EOF
# Release ${VERSION} - Pre-Submission Version

This release contains the pre-submission version of the Ethical Riemann Hypothesis paper.

## Contents

- **English PDF**: \`ethical_riemann_hypothesis_en.pdf\`
- **Chinese PDF**: \`ethical_riemann_hypothesis_zh.pdf\`
- **Supplementary Material**: \`supplementary_material.tar.gz\`
  - Experiment reports (\`docs/EXPERIMENT_REPORTS.md\`)
  - Simulation outputs (\`simulation/output/\`)
  - Real-data case studies (\`data/\`)
  - Generated figures (\`figures/\`)

## Key Changes in This Version

- Unified ERH terminology: "Within ERH-style bound?" and "Near-critical ERH regime?"
- Added Remark in Section 4.1: ERH as necessary but not sufficient condition
- Enhanced Table 4 with "ERH-style bound" and "Overall verdict" columns
- Added multi-seed stability table (Section 5.5)
- Added real-data comparison table (Section 6.6)
- Updated Figure 6 caption to align with actual plot content
- Added operational recommendations for AI governance (Section 7.6)
- Enhanced supplementary material references throughout
- Created README_for_reviewers.md for reviewer guidance
- Added psychohistory technical documentation

## For Reviewers

See \`README_for_reviewers.md\` in the main repository for:
- How to reproduce experiments
- Location of supplementary material
- Quick review guide

## Next Steps

1. Review the PDFs for final formatting
2. Verify all figures are correctly generated
3. Test reproduction instructions
4. Create GitHub release with these files attached
EOF

echo "✓ Created RELEASE_NOTES.md"

echo ""
echo "Release preparation complete!"
echo "Release files are in: ${RELEASE_DIR}/"
echo ""
echo "Next steps:"
echo "1. Review the files in ${RELEASE_DIR}/"
echo "2. Create a GitHub release tag: git tag -a ${VERSION} -m 'Pre-submission version'"
echo "3. Push the tag: git push origin ${VERSION}"
echo "4. Create a GitHub release and upload files from ${RELEASE_DIR}/"

