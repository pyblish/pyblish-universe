#!/usr/bin/env bash
gunicorn app.app:app --log-file -