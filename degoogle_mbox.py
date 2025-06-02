import mailbox
import argparse
from datetime import datetime, timezone
import re
import email.utils
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_date(date_str):
    """Try to parse date string using multiple formats."""
    if not date_str:
        return None
    
    # First try email.utils parser
    try:
        return email.utils.parsedate_to_datetime(date_str)
    except (TypeError, ValueError):
        pass

    # Common date formats to try
    formats = [
        "%Y/%m/%d",                     # 1996/03/19
        "%a, %d %b %Y %H:%M:%S %z",    # Thu, 21 May 1998 05:33:29 -0500
        "%d %b %Y %H:%M:%S %z",        # 21 May 1998 05:33:29 -0500
        "%a %b %d %H:%M:%S %Y",        # Thu May 21 05:33:29 1998
        "%Y-%m-%d %H:%M:%S",           # 1998-05-21 05:33:29
        "%Y-%m-%d",                     # 1998-05-21
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None

def fix_date(date_str):
    """Try to parse and fix the date string."""
    parsed = parse_date(date_str)
    if parsed:
        return parsed

    # Try to extract date components using regex
    patterns = [
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',      # Month DD, YYYY
    ]

    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                groups = match.groups()
                if len(groups[0]) == 4:  # YYYY/MM/DD format
                    dt = datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                else:  # Other formats
                    dt = datetime(int(groups[2]), 1, 1)  # Default to January 1st if month/day unclear
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    
    return None

def fix_dates_in_mbox(input_file, output_file):
    """Process mbox file and fix date headers, remove Google headers and fix From_ lines."""
    try:
        # Read the input file as text first to handle the From_ lines
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Count the Google From lines (including at start of file)
        fixed_from_lines = len(re.findall(r'(?:^|\n)From -?\d+(?:\n|$)', content))
        
        # Write to a temporary file that we'll use to create the mbox
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp_name = temp.name
            
            # Split into messages (Google's From separator), handling first line
            messages = re.split(r'(?:^|\n)From -?\d+\n', content)
            
            for msg_content in messages:
                if not msg_content.strip():
                    continue
                    
                # Parse the message to extract From and Date
                msg = email.message_from_string(msg_content)
                from_header = msg.get('From', 'MAILER-DAEMON')
                date_str = msg.get('Date')
                
                # Parse the email address from From header
                from_addr = email.utils.parseaddr(from_header)[1] or 'MAILER-DAEMON'
                
                # Parse and format the date
                try:
                    date = fix_date(date_str)
                    if date is not None:
                        date_str = date.strftime('%a %b %d %H:%M:%S %Y')
                    else:
                        date_str = 'Thu Jan 1 00:00:00 1970'
                except (AttributeError, ValueError):
                    date_str = 'Thu Jan 1 00:00:00 1970'
                
                # Write proper mbox From_ line and cleaned message content
                temp.write(f"From {from_addr} {date_str}\n")
                temp.write(msg_content.strip() + "\n\n")
        
        # Now process the mbox to clean up headers
        mbox = mailbox.mbox(temp_name)
        fixed_messages = []
        total = 0
        fixed_dates = 0
        removed_google_headers = 0
        preserved_threading = 0
        
        for message in mbox:
            total += 1
            
            # Fix dates
            if 'Date' in message:
                original_date = message['Date']
                fixed_date = fix_date(original_date)
                if fixed_date:
                    fixed_dates += 1
                    fixed_date_timestamp = int(fixed_date.timestamp())
                    message.replace_header('Date', email.utils.formatdate(fixed_date_timestamp, usegmt=True))
            
            # Preserve threading headers before removing Google headers
            threading_headers = {
                'References': message.get('References', ''),
                'In-Reply-To': message.get('In-Reply-To', ''),
                'Message-ID': message.get('Message-ID', '')
            }
            
            # Remove X-Google headers
            google_headers = [k for k in message.keys() if k.startswith('X-Google-')]
            for header in google_headers:
                del message[header]
                removed_google_headers += 1
            
            # Restore threading headers if they existed
            for header, value in threading_headers.items():
                if value:
                    message[header] = value
                    preserved_threading += 1
            
            fixed_messages.append(message)
        
        # Save the fixed messages
        new_mbox = mailbox.mbox(output_file)
        new_mbox.lock()
        try:
            for msg in fixed_messages:
                new_mbox.add(msg)
        finally:
            new_mbox.unlock()
            new_mbox.close()
        
        # Clean up temporary file
        import os
        os.unlink(temp_name)
        
        logger.info(f"Processed {total} messages, fixed {fixed_dates} dates")
        logger.info(f"Removed {removed_google_headers} X-Google headers")
        logger.info(f"Fixed {fixed_from_lines} Google From lines")  # Add new log line
        
    except Exception as e:
        logger.error(f"Error processing mbox file: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Fix date headers in an mbox file.")
    parser.add_argument('input_file', help='Path to the input mbox file')
    parser.add_argument('output_file', help='Path to save the output mbox file')
    args = parser.parse_args()
    
    fix_dates_in_mbox(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
