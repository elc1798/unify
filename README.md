# Unify

Unify is an backend web application to link together all of your commonly used
chat / instant messaging services. The intention is to let you unify a FaceBook
chat, IRC channel, etc. and be able to receive and send messages to all of them
at the same time, unifying them.


## Setting up a private IRC channel for this

Choose a nickname for your bot, and **register** the name:

```
/msg nickserv register your_password your_email_address
```

Register a private channel:

```
/msg chanserv register <channel>
/msg chanserv set <channel> guard on (Chanserv will join your channel)
/mode <channel> +i (set channel to invite only)
/msg chanserv access <channel> add <nick> (for each person that should be able to join)
/mode <channel> +I <nick> (for each person that should be able to join)
/msg chanserv FLAGS <channel> <nick> +V (for each person that should be able to chat)
```

