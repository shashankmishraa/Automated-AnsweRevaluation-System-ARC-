import re

# Read the file
with open('ui-react/app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position to insert (after extractedText section)
insert_marker = '''        ${result.extractedText ? `
        <div class="details-section">
            <h3>📝 Extracted Text (OCR)</h3>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; line-height: 1.8; color: #555;">
                ${result.extractedText}
            </div>
        </div>
        ` : ''}'''

# New content to add
new_section = '''
        ${result.question || result.studentAnswer ? `
        <div class="details-section" style="background: #f8f9fa; border-top: 2px solid #e0e0e0;">
            <h3>📝 Evaluation Details</h3>
            
            ${result.question ? `
            <div style="margin-bottom: 24px;">
                <h4 style="color: #667eea; margin-bottom: 12px; font-size: 18px;">❓ Question:</h4>
                <div style="background: white; padding: 20px; border-radius: 8px; line-height: 1.8; color: #555; border-left: 4px solid #667eea;">
                    ${result.question}
                </div>
            </div>
            ` : ''}
            
            ${result.studentAnswer ? `
            <div style="margin-bottom: 24px;">
                <h4 style="color: #667eea; margin-bottom: 12px; font-size: 18px;">✍️ Student Answer:</h4>
                <div style="background: white; padding: 20px; border-radius: 8px; line-height: 1.8; color: #555; border-left: 4px solid #4CAF50;">
                    ${result.studentAnswer}
                </div>
            </div>
            ` : ''}
            
            ${result.referenceAnswer ? `
            <div style="margin-bottom: 24px;">
                <h4 style="color: #667eea; margin-bottom: 12px; font-size: 18px;">✅ Reference Answer:</h4>
                <div style="background: white; padding: 20px; border-radius: 8px; line-height: 1.8; color: #555; border-left: 4px solid #FF9800;">
                    ${result.referenceAnswer}
                </div>
            </div>
            ` : ''}
        </div>
        ` : ''}'''

# Insert the new content
if insert_marker in content:
    updated_content = content.replace(insert_marker, insert_marker + new_section)
    
    # Write back
    with open('ui-react/app/page.tsx', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Successfully added Question, Student Answer, and Reference Answer!")
    print("")
    print("Next steps:")
    print("1. Refresh your browser (Ctrl+Shift+R)")
    print("2. Test text evaluation") 
    print("3. Download HTML report - it will now show all content!")
else:
    print("❌ Could not find the insertion point!")
    print("Please make sure the file structure matches.")
