# Demo PMCP Server with Claude Desktop and GMAIL

This application runs a server in WSL bridging Calude Desktop and Gmail to read emails and draft replies.  

The application has been designed strictly as readonly for the purpose of a demo and has the API scope of gmail.readonly  

Further modifications would involve sending, folder moving and marking as junk.  

Note that I included a note "This email was generated with Claude..." on the draft emails.  

# Gotchas
1. In order to respond with both the unread emails and the recent emails Claude needs a specific description, I included the advise to use the recent emails for a summary rather than unread.
2. The readonly aspect means an email will remain in readonly mode even when it is effectively read on Calude (though not on gmail). This is left as-is for the demo app and is easily resolved with modify scope.
3. It doesn't like to refersh, so if a new email comes in during a session you won;t see unless you explicitly ask to refresh. This limitation is known and could be resolved with the description, and with the explicit promting.

## Interaction
**Example Prompts**  
- Reading emails  
"Show me my unread emails"  
"Get me my last 10 emails"  
"What emails have I received today?"  
"Read my most recent 5 emails"  

- Drafting replies  
"Draft a reply to [sender] saying I'll get back to them tomorrow"  
"Reply to the email from [sender] and decline politely"  
"Write a reply to [subject] email saying yes I can make the meeting"  

- Composing new emails  
"Draft a new email to john@example.com asking about the project deadline"  
"Write an email to my team announcing the meeting is cancelled"  

- Combining both  
"Read my unread emails and draft a polite reply to any that need a response"  
"Check my emails and summarise what needs my attention"  


## Screen shots
![alt text](images/image.png)
![alt text](images/image-1.png)
![alt text](images/image-2.png)
![alt text](images/image-3.png)
![alt text](images/image-4.png)
![alt text](images/image-5.png)