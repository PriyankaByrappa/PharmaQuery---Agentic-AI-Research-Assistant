#!/bin/bash
# Script to install Playwright browsers

echo "Installing Playwright browsers..."
echo "This may take a few minutes..."

pip install playwright
playwright install chromium

echo "✅ Playwright installation complete!"





