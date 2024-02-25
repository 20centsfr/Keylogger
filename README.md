# Keylogger Project

## Disclaimer
This project is intended for educational and research purposes only. The use of this software for monitoring or accessing unauthorized data without proper consent may violate local, state, or federal law. The authors of this software are not responsible for any misuse or damage caused by the usage of this software.

## Overview
This project is a keylogger designed to capture all keystrokes made by the user and send them to a server. The server-side component of the project provides a set of commands to manage and interact with the keylogger.

## Usage

### Client (Keylogger)
The keylogger should be executed on the target system to capture keystrokes. It operates silently in the background.

### Server
The server component provides a set of commands to interact with the keylogger:

help: Displays a list of available commands.
kill: Stops all instances of the server.
show: Displays the list of received files.
readfile <filename>: Displays the content of the specified file.
listen <port>: Puts the server in listening mode on the specified TCP port.
