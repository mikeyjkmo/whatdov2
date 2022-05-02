# WhatDo? (V2)

WhatDo is an app that helps to prioritise the things you need to do. At any given
time, it will provide you with the **single most important task** you should be
doing right now. It does this using a weighted shorted-processing time algorithm.

Features supported:
* Tasks can be made dependent on other tasks
* Tasks can be activated at later dates

## Architecture

WhatDo is inspired by "Clean Architecture" -- however, its pure domain model is
immutable and composed of pure functions.
