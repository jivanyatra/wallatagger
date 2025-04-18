# Wallatagger

Wallatagger is a tool that helps you automatically tag articles.

## Use Case

Suppose you are a [Wallabag](https://github.com/wallabag/wallabag) user.

Suppose you bag articles from a website you frequent. Their articles have links to their own site tags in the body. You want to use those tags.

Suppose you want to do it automatically.

*Wallatagger has entered the chat.*

## How It Works

Wallatagger uses a [`.env`](.env.example) file. You fill it out, and then you set the Wallatagger container to run according to whatever frequency you want (either via SystemD, or Cron, or whatever).

It will then:
1. use the API credentials to fetch all articles since the last timestamp
1. parse the article body for the regex you specify
1. grab the "capture group" out of the regex matches as tags
1. dedupe the tags (only exact copies) and alphabetize them
1. update the article via API to include those tags
1. after processing all entries, it will update the timestamp

You can specify the log level if you like.

## Caveats

This is very much a work in progress. Things might change pretty drastically - like variable names in the `.env` file for configuration, how logging works, how the regex capturing system works... Even the deployment via Docker may change.

## License

[MIT License](LICENSE), so the license file needs to be included (which, I guess, gives me some minimal attribution). Aside from that: do what you want with it, but you can't blame me for anything that happens.

## Developer Stuff

If you find problems, please feel free to open an issue and discuss. If you'd like to collaborate, please reach out! To grab my attention, feel free to use the subject line "Wallatagger COLLAB" and I'll try to get back to you ASAP. This project is fun and I have a personal need for it, but it's not a priority.

I have specified some [Developer Notes](DEV_NOTES.md) that I gathered as a started the project.

Some weird things to note:
* TODO

Build command:
```
docker build -t wallatagger:0.1.1 --no-cache .
```

Single run command:
```
docker run --rm -it --env-file .env --network=host --entrypoint /bin/sh wallatagger:0.1.1
```

Assuming wallabag instance is running in another container somewhere...

### TO DO:

1. When checking for existing tags, make sure that out of the set of scraped tags, each one is present in the set of existing tags. Only then skip. Right now, if extra tags are present on an article, it will reparse and update tags because the strings don't match.
1. ~~Figure out pagination!~~
1. Add a function to only regrab if it's not a 404! Wallabag doesn't do this SMH
1. Change the storage of config from environment vars to config file; docker won't write env vars back to the outside env.