# Halite Bot
"[Halite](https://halite.io/) is an open source artificial intelligence programming challenge, created by Two Sigma, where players build bots using the coding language of their choice to battle on a two-dimensional virtual board. This year's game is a space story. Your mission is to extract Halite. Bots control ships that dock on and mine planets, producing more ships to defeat opponents. To achieve victory, you will need optimal pathfinding and swarm control to move efficiently from planet to planet and destroy enemy ships."

After achieving minimal success trying to dock the closest and largest planets, my strategy was to delegate different ships to different jobs (attack, protect) in order to attack other ships while they are expanding to the planets. At time of writing, my bot achieved a rank of49/1802 for university students and 185/4182 overall.

# How to run 
In order to challenge two bots against each other, run:
```python
./halite -d '160 160' -t 'python3 MyBot.py' 'python3 TestBot.py'
```

