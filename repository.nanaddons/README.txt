HOW COMMUNITY PORTAL REPO WORKS:
No add-ons are physically uploaded to the repository, it is just a placeholder which
mirrors the content found on other repo's. If you would like your repository added
so it shows up in here then please take a look at the following rules. Sorry we hate
to enforce rules but don't worry these are pretty straight forward ones with only
the end users in mind.

RULES WILL BE RULES - We only have 5 of them....

1. No repositories will be accepted that contain others re-uploaded work (using the same
add-on id as the original) unless you can supply written proof that the original developer
has given their consent for you to re-upload. This of course does not include forks, if
you're forking an existing add-on and changing code then of course that's allowed but you
MUST make sure you're using a new unique ID that's not already in use. You can either
search for the id you're intending to use at http://noobsandnerds.com/addons or you can
use the Add-on Creator at http://totalrevolution.tv which will check to see whether or
not your id is free to use.

2. If you want your add-ons visible on this repo then you must offer some kind of support
to your users. If you don't want to use the noobsandnerds forum for offering support that
is completely fine and entirely your choice but you will still be required to create a
release thread on there. This can be a closed thread (so nobody can reply) if that's
what you prefer but it must contain details of where users can go for the support.

We are non-restrictive at NaN so you can direct support wherever you want, whether that's
your own website, another kodi based forum, Facebook, Twitter... so long as you have
a dedicated arena for support you can link to it. If you choose to use the noobsandnerds
forum for your support you must abide by the simple rules laid out there, it's basically
all about everyone getting along and having fun but do check them out:
http://www.noobsandnerds.com/support/showthread.php?tid=27

4. Under NO circumstances will malicious code will be tolerated. Failure to adhere to this
condition will result in your repo being immediately pulled from the Community Portal
Repo and the NaN source. Depending on the severity of the code and if found to be
intentional you could end up with your repo/add-ons being blacklisted on the Add-on
Portal.

5. No add-ons that are officially supported in the Kodi.tv repository will be accepted.
There is a very valid reason for this, please read below:

Reuploading any content found on the kodi repo will automatically get your repo put on a
blacklist at NaN when the Addon Portal performs it's daily scan for new content. Whilst
this will not affect users installing your content or downloading your repo they will be
warned of possible side-effects.

IMPORTANT: The reason for this is kodi has separate repo's for different versions of
Kodi/XBMC and often they keep the exact same id but have a completely different version in
each repo. As we've seen plenty of times before, installing the wrong version on a system
can make the system act very weird - a prime example was the common cache and simple
downloader modules which a lot of people had reuploaded to their repos. Kodi would
automatically update the add-on from repo x and it wasn't designed for the currently
running version of Kodi which meant LOTS of add-ons on the system could not update
and it even hampered the system accessing certain sites.

AN EXCEPTION TO THE RULE:
script.module.urlresolver

^ That is a module officially supported at kodi.tv BUT this and script.extendedinfo
are currently the only exceptions to the rule about re-uploading content from
the kodi.tv repo (if you know of more please do let us know).

The reason for this is the original developers of those addons had given permission to
Eldorado (TVA) and Quihico (NaN) to fork them and keep the same id. I think the
understanding was there are already so many addons hooking into those id's that it made 
sense to keep the existing id.

There's an automated solution which would make life much easier for you when it comes to
using TVAddons modules. Take a look at the TVA repository addon.xml file and you'll notice
they have 2 sources to scan in there rather than just the one, just copy the TVA Common
section and make sure you add the <dir> tags as they've done. Now no longer do you have to
manually attempt to keep up with things like urlresolver, it will now install directly
from their source.

If you need any help please contact a member of the development team at noobsandnerds.com

PYTHON KODING:
Top Tip: If you want to use the Python Koding framework for your add-ons then that's
great, it's designed for everyone to use regardless of where they support their add-ons.
However if you choose to offer full support of your add-on exclusively at noobsandnerds
you will have access to the unique features which hook into our servers. There's some
really great features you can use but we can't offer it to everyone.

The more users hooking into our servers the more our server costs go up, this is the
reasoning behind this decision. We feel if you offer support exclusively at NaN then the
extra traffic coming through the website should hopefully counter-balance the extra costs
required for servers (via the google ads). Or at least that's the theory!

We hope to see you over at noobsandnerds.com very soon!
