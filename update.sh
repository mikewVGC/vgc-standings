#!/bin/bash

git pull --rebase origin main
git submodule update --remote --merge
