                                  __              __        ___  ___
          _      ________      __/ /_  __  ______/ /  _   _<  / <  /
         | | /| / / ___/ | /| / / __ \/ / / / __  /  | | / / /  / / 
         | |/ |/ (__  )| |/ |/ / / / / /_/ / /_/ /   | |/ / /_ / /  
         |__/|__/____/ |__/|__/_/ /_/\__,_/\__,_/    |___/_/(_)_/   
                                                                     
Author: stylemistake@gmail.com

-----------------------------------------------------------------------------
   About software

This is an external HUD with item timers for Warsow.

Basically it's a self-hosted Web app, so you can open it on whatever you
want (iPad or second monitor - you choose)


-----------------------------------------------------------------------------
   Usage

Include "wswhud/proto_pixcode.hud" into your favourite hud.
Or just copy "guwashi_ext.pk3" to your basewsw, and you should be ok (select
"guwashi_ext" in game options)

Launch "wswhud_app.exe" on Windows. (everything is built-in)
Launch "python wswhud_app.py" on Linux (depends on pygtk)

Usage: wswhud_app <options>
Options:
    -p --port <n>: Server port (default: 44100)
    -f --freq <n>: Protocol update frequency, in Hz (default: 4)
        Higher value increases hud precision at cost of some game lag
        Reasonable values are between 2-8 (+-250ms to +-62ms precision)

To test if everything works, point browser at:

  http://localhost:44100/

You can access this from your smartphone or tablet!
Point to your PC's local IP address, usually 192.168.1.***

  http://192.168.1.***:44100/

Tap anywhere on the page to go fullscreen.


-----------------------------------------------------------------------------
   Known bugs

Currently app works only through pixcode protocol.
This can introduce some latency to final readings and sometimes to Warsow.

To fix stutter in Warsow, limit FPS with cl_maxfps to refresh rate of your
monitor. Another option is to turn on VSync. That helps a lot, won't lie,
since app grabs some frames :3

If timers are slow (or too fast), try to run tests to check if everything
is consistent. (wswhud_proto_pixcode_test.py). If not, report me by email.
Usually restarting the wswhud_app solves all issues.

Server startup in my Windows setup is kinda long, and seems it's some nasty
stuff with Windows firewall.


-----------------------------------------------------------------------------
   Build for Windows

Set up Python, Pip and PyGTK, then:

  pip install pyinstaller
  build.bat


-----------------------------------------------------------------------------
   Misc

This is not a cheat, this is just a basic helper :).
Good timing is only a tiny little bit of a great skill.
If you suck at duels, this won't help... :3

GL & HF!
