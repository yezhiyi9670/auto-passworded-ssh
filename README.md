# apssh: Auto-passworded SSH

![Not so secure: Avoid whenever possible](https://img.shields.io/badge/Not%20so%20secure-Avoid%20whenever%20possible-orange?style=flat-square)
![Supports Unix-like systems and Windows](https://img.shields.io/badge/Supports-Unix--like%20systems%20and%20Windows-blue?style=flat-square)

This is a simple wrapper of the `ssh` and `scp` commands that auto-fills password and verification code (TOTP) during SSH log-in, so that you do not need to type in your password and verification code every time.

> [!WARNING]
>
> If you are fed up with typing the passwords, ALWAYS avoid this and prefer proper passwordless login with [public key authentication](https://www.redhat.com/en/blog/key-based-authentication-ssh) whenever possible.
>
> Auto-filling password and verification code requires storing your password and OTP seed, which is NOT a good security practice. Auto-filling your OTP from the same source as the password also defeats the purpose of the "second-factor" authentication.
>
> This tool is only intended for you if you do not want to type passwords AND the server you have to log into cannot support proper public key authentication at all.
>
> Your warranty is now void. USE AT YOUR OWN RISK.

## Setup

1. If you are using Windows, make sure you have a working \*nix-style shell `sh.exe` in your PATH since the wrapper is a shell script.
   - One way is to use Git Bash shipped with Git for Windows. The appropriate binary is the wrapper binary at `$GIT_INSTALL_DIR/bin/sh.exe`, not `$GIT_INSTALL_DIR/usr/bin/sh.exe`.
2. In your system's default Python3 installation (`python3`), install the `ruyaml` and `pyotp` packages.
3. Clone or download repository to wherever you want.
4. Add the `bin` folder to your PATH (Use environment variable settings in Windows and bash/profile for *nix).
5. Test installation with command `apssh -V`.

## Usage

You can use the `apssh` and the `apscp` commands in the way you would use `ssh` and `scp`. They will prompt for passwords in the normal way if a stored password is not provided:

```
$ apssh ServerName
(username@11.4.5.14) Password:
(username@11.4.5.14) Verification code:
```

Stored passwords and OTP seeds will be loaded from files `~/.ssh/apssh_passwords.yml` and `~/.ssh/apssh_passwords.d/*.yml`. See  [this file](./doc/apssh_passwords.example.yml) for an example. When a stored password is present for the username-server combination, `apssh` and `apscp` will no longer prompt for passwords, but will show something like this:

```
$ apssh ServerName
[AUTO] (username@11.4.5.14) Password ********
[AUTO] (username@11.4.5.14) Verification code ***389
user@hostname:~$
```

The password auto-responder currently enforces a short and random delay before responding the password or verification code to avoid potential issues caused by overly fast interaction.

> [!CAUTION]
>
> Make sure that you set yourself as the owner of the stored password YAML files and restrict their permissions so that other users will not be able to read them.
>
> The wrapper currently does not check if the permssions are secure, so take care of your own security.

## Use with VSCode Remote-SSH

To make VSCode Remote-SSH benefit from the auto-fill (so VSCode no longer asks for password every time you open a folder or reconnect), you can set the `Remote.SSH: Path` item (`remote.SSH.path`) in your VSCode settings to the absolute path of the `apssh` wrapper executable. Use the `bin/apssh` on \*nix systems and `bin/apssh.cmd` on Windows.

## Limitations

- Only cleartext passwords and six-digit OTPs are supported.
- Only password/code prompts that take the form of `(<username>@<address>)<the_rest>` or `(<address>)<the_rest>` can be recognized. The text in the parenthesis will be used as the user-server combination used to look up the stored password, and `<the_rest>` will be matched against the trigger phrase.
- The wrapper makes use of environment variables `SSH_ASKPASS`, `SSH_ASKPASS_REQUIRE` and `DISPLAY`, meaning that existing SSH_ASKPASS configuration provided by the system (for example, by your desktop environment) will not be effective when using the wrapper.
