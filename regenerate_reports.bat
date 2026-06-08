@echo off
echo ===================================================================
echo          REGENERATE ALL SCORING REPORTS
echo ===================================================================
echo.

echo [1/3] Generating static scoring report...
python generate_static_score.py
if errorlevel 1 (
    echo ERROR: Failed to generate static score report
    pause
    exit /b 1
)

echo.
echo [2/3] Generating HTML visual report...
python generate_html_report.py
if errorlevel 1 (
    echo ERROR: Failed to generate HTML report
    pause
    exit /b 1
)

echo.
echo [3/3] Opening HTML report in browser...
start score_report.html

echo.
echo ===================================================================
echo                    ALL REPORTS GENERATED!
echo ===================================================================
echo.
echo Files created:
echo   - static_scoring_report.json  (detailed data)
echo   - score_report.html           (visual report card)
echo.
echo The HTML report should now be open in your browser.
echo If not, manually open: score_report.html
echo.
echo ===================================================================
pause
