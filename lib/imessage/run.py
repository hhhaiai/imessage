import applescript

def send_imessage(recipient, message):
    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set theBuddy to buddy "{recipient}" of targetService
        send "{message}" to theBuddy
    end tell
    '''
    applescript.run(script)

# 使用示例
send_imessage("+8615510010000", "https://airmessage.org/")
send_imessage("+8615510010000", "Hello 133!")
send_imessage("hello@gmail.com", "https://www.beeper.com/download")
