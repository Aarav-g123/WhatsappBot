import re
import sys
from datetime import datetime

def get_last_day_messages(input_file):
    """Extract messages from the last day in the chat log"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    messages = []
    last_date = None
    
    for line in lines:
        line = line.strip()

        match = re.match(r'(\d{1,2}/\d{1,2}/\d{2}),', line)
        if match:
            try:
                date_str = match.group(1)
                date_obj = datetime.strptime(date_str, '%m/%d/%y')
                messages.append((date_obj.date(), line))

                if last_date is None or date_obj.date() > last_date:
                    last_date = date_obj.date()
            except:
                continue
    
    if not messages:
        return [], None
    

    last_day_msgs = [msg[1] for msg in messages if msg[0] == last_date]
    return last_day_msgs, last_date

def replace_names(messages, name_map):
    """Replace sender names in messages"""
    if not name_map:
        return messages
    
    replaced_messages = []
    for line in messages:
        for old_name, new_name in name_map.items():

            line = re.sub(rf'- {re.escape(old_name)}:', f'- {new_name}:', line)
        replaced_messages.append(line)
    
    return replaced_messages

def save_and_print(messages, output_file, title="Messages"):
    """Save messages to file and print to console"""
    print(f"\n{title}:")
    print("=" * 60)
    
    for msg in messages:
        print(msg)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(messages))
    
    print(f"\nSaved {len(messages)} messages to '{output_file}'")

def main():
    """Interactive chat log processor"""
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter input filename (default: input.txt): ").strip()
        if not input_file:
            input_file = "input.txt"
    
    try:
        messages, last_date = get_last_day_messages(input_file)
        
        if not messages:
            print("❌ No valid messages found in the file.")
            return
        
        print(f"\n📅 Found messages from {last_date.strftime('%m/%d/%y')}")
        print(f"📝 Total messages: {len(messages)}")
        
        # Ask about name replacement
        replace_names_option = input("\nReplace names? (y/n, default: n): ").strip().lower()
        name_map = {}
        
        if replace_names_option == 'y':
            print("\nEnter name replacements (format: old_name new_name)")
            print("Example: 'Billy Eilish Bill' or 'Jeff Adams'")
            print("Press Enter twice when done:")
            
            while True:
                replacement = input("> ").strip()
                if not replacement:
                    break
                
                parts = replacement.split()
                if len(parts) >= 2:
                    old_name = ' '.join(parts[:-1])
                    new_name = parts[-1]
                    name_map[old_name] = new_name
                    print(f"  Will replace '{old_name}' with '{new_name}'")
                else:
                    print("  Format: old_name new_name")

        if name_map:
            messages = replace_names(messages, name_map)
            print("\n✅ Names replaced successfully")

        output_file = input(f"\nOutput filename (default: output.txt): ").strip()
        if not output_file:
            output_file = "output.txt"
        
        save_and_print(messages, output_file, f"Last day messages ({last_date.strftime('%m/%d/%y')})")
        
        open_file = input("\nOpen the output file? (y/n, default: n): ").strip().lower()
        if open_file == 'y':
            try:
                import os
                os.startfile(output_file)  # Windows
            except:
                try:
                    import subprocess
                    subprocess.call(['open', output_file])  # macOS
                except:
                    try:
                        import subprocess
                        subprocess.call(['xdg-open', output_file])  # Linux
                    except:
                        print(f"Can't open automatically. File saved at: {output_file}")
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()