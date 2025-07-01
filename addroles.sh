#!/bin/bash
for i in $(ls | grep ludus); do ludus ansible role add -d "$i"; done
