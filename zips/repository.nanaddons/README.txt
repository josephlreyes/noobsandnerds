HOW COMMUNITY PORTAL REPO WORKS:
No add-ons are physically uplaoded to the repository, it is just a placeholder which
mirrors the content found on other repo's. If you would like your repository added
so it shows up in here then please take a look at the following rules. Sorry we hate
to enforce rules but don't worry these are pretty straight forward ones with only
the end users in mind.

RULES WILL BE RULES - We only have 4 of them....

1. No repositories will be accepted that contain others re-uploaded work (using the same
add-on id as the original) unless you can supply written proof that the original developer
has given their consent for you to re-upload. This of course does not include forks, if
you're forking an existing add-on and changing code then of course that's allowed but you
MUST make sure you're using a new unique ID that's not already in use. You can either
search for the id you're intending to use at http://noobsandnerds.com/addons or you can
use the Add-on Creator at http://totalrevolution.tv which will check to see whether or
not your id is free to use.

2. If you want your add-ons to show in the featured/recommended section of the Add-on Portal
then you must offer some kind of support to your users. If you don't want to use the noobsandnerds
forum for offering support that is completely fine and entirely your choice but you will need to
either add a forum link in your addon.xml or directly add a forum link via the Edit Add-on option
on the Add-on Portal. This can needs to be a link to wherever you choose to offer support, whether
that's your own personal website or another forum the choice is entirely yours.

We are non-restrictive at NaN so you can direct support wherever you want, whether that's
your own website, another kodi based forum, Facebook, Twitter... so long as you have
a dedicated arena for support you can link to it. If you choose to use the noobsandnerds
forum for your support you must abide by the simple rules laid out there, it's basically
all about everyone getting along and having fun but do check them out:
http://www.noobsandnerds.com/support/showthread.php?tid=27

3. Under NO circumstances will malicious code will be tolerated. Failure to adhere to this
condition will result in your repo being immediately pulled from the Community Portal
Repo and the NaN source. Depending on the severity of the code and if found to be
intentional you could end up with your repo/add-ons being blacklisted on the Add-on
Portal.

4. No repos containing content officially supported by Kodi.tv and reuploaded 
will be accepted. Reuploading any content found on the kodi repo will automatically get
your repo put on a blacklist at NaN when the Addon Portal performs it's daily scan for new
content. Whilst this will not affect users installing your content or downloading your repo
they will be warned of possible side-effects.

IMPORTANT: The reason for this is kodi has separate repo's for different versions of
KodiXBMC and often they keep the exact same id but have a completely different version in
each repo. As we've seen plenty of times before, installing the wrong version on a system
can make the system act very weird - a prime example was the common cache and simple
downloader modules which a lot of people had reuploaded to their repos. Kodi would
automatically update the add-on from repo x and it wasn't designed for the currently
running version of Kodi which meant LOTS of add-ons on the system could not update
and it even hampered the system accessing certain sites.


TOP TIPS:
=========
PYTHON KODING:
If you want to use the Python Koding framework for your add-ons then that's great, it's
designed for everyone to use regardless of where they support their add-ons. However if
you choose to offer full support of your add-on exclusively at noobsandnerds you will have 
access to the unique features which hook into our servers. There's some really great
features you can use but sadly we can't offer them to anyone outside of the NaN camp.

The reasoning behind this decision is a simple one - the more users hooking into our
servers the more our server costs go up. Imagine if every box seller out there was
hooking into the system, we just wouldn't be able to afford to server costs associated
with such a huge amount of traffic.

For this reason we feel it's only fair to limit the unique features to NaN developers, if
you offer support exclusively at NaN then the extra traffic visiting the website for
support should hopefully counter-balance the extra costs required for servers (via the
google ads). Or at least that's the theory!

HOOKING INTO THIRD PARTY MODULES:
There's an automated solution which would make life much easier for you when it comes to
using TVA and NaN modules. You can just add those repo directories into your repository addon.xml file. Take a look at the example below.

Thanks for reading and we hope to see you over at noobsandnerds.com very soon!


REPOSITORY ADDON.XML:

<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="repository.myrepo" name="my repository" version="1.0" provider-name="nan">
	<extension point="xbmc.addon.repository" name="my repository">
	<dir>
		<info compressed="false">https://offshoregit.com/tvaresolvers/tva-common-repository/raw/master/addons.xml</info>
		<checksum>https://offshoregit.com/tvaresolvers/tva-common-repository/raw/master/addons.xml.md5</checksum>
		<datadir zip="true">https://offshoregit.com/tvaresolvers/tva-common-repository/raw/master/zips/</datadir>
	</dir>
	<dir>
		<info compressed="false">https://raw.githubusercontent.com/noobsandnerds/modules4all/master/zips/addons.xml</info>
		<checksum>https://raw.githubusercontent.com/noobsandnerds/modules4all/master/zips/addons.xml.md5</checksum>
		<datadir zip="true">https://raw.githubusercontent.com/noobsandnerds/modules4all/master/zips/</datadir>
	</dir>
		<info compressed="false">https://raw.githubusercontent.com/myrepo/repository.myrepo/master/addons.xml</info>
		<checksum>https://raw.githubusercontent.com/myrepo/repository.myrepo/master/addons.xml.md5</checksum>
		<datadir zip="true">https://raw.githubusercontent.com/myrepo/repository.myrepo/master/zips/</datadir>
	</extension>
	<extension point="xbmc.addon.metadata">
		<summary>My test repo</summary>
		<description>Example repo addon.xml for importing common modules from TVA and NaN</description>
		<platform>all</platform>
	</extension>
</addon>

