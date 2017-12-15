#!/usr/bin/env bash

echo "Removing /kb/parsers..."
ssh indeni@10.0.0.10 rm -rf /usr/share/indeni-collector/kb/parsers/

echo "Copying new parsers..."
scp -rpq ~/projects/indeni/indeni-knowledge/parsers/ indeni@10.0.0.10:/usr/share/indeni-collector/kb/

echo "Restarting server..."
ssh -t indeni@10.0.0.10 "sudo /etc/init.d/indeni-collector restart"

echo "Done."
