# FindMySpot

This is a useful Python script to spoof the location of an Apple device to any location through a specific address or coordinate.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Make sure you have [Python](https://www.python.org/) installed.
This was script was developed with Python version 2.7.10.

```
python
```


### Running the Script

Make sure you navigate to the correct directory,

```
cd
```

and then to check that you're in the correct directory,

```
pwd
```


## Deployment on a server

The script terminates if the terminal / command-line window closes.

In order for the script to continue running and continue spoofing its location. You would have to host the script and run it from a server.

My personal set up is through a [DigitalOcean](https://www.digitalocean.com/) Ubuntu Droplet. For my script to continue to run after I exit out of the Command Line Interface, I use [tmux](https://hackernoon.com/a-gentle-introduction-to-tmux-8d784c404340).
