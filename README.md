# Instructions
* See the .py file
* Run sep_by_length to separate words by length
# Sample befores and afters
By types of lines (non-exhaustive, there may be mixes of each)
### zero derivatives
```
AE one [adj]
```
becomes
```
AE$one [adj]
```
---
### one derivative
```
AA rough, cindery lava [n AAS]
```
becomes
```
AA$rough, cindery lava [n AAS]
```
---
### 2+ derivaties
```
AH {aah=v} [v AHED, AHING, AHS]
```
becomes
```
AH$AAH (v) to exclaim in amazement, joy, or surprise [v AHED, AHING, AHS]
```
---
### {} (Synonym of another word)
```
AD an {advertisement=n} [n ADS]
```
becomes
```
AD$an ADVERTISEMENT (n) (no description) [n ADS]
```
---
### <> (form of another word, points to root word)
```
AM <be=v> [v]
```
becomes
```
AM$BE (v) to have actuality [v]
```
---
### / (multiple meanings, 2+)
```
OS a bone [n OSSA] / an {esker=n} [n OSAR] / an {orifice=n} [n ORA]
```
becomes
```
OS$a bone [n OSSA]<br>an ESKER (n) a narrow ridge of gravel and sand [n OSAR]<br>an ORIFICE (n) a mouth or mouthlike opening [n ORA]
```
# Notes
* Sorts by length then alpha
* \<br> is a line break in Anki (for multiple forms/"meanings"), $ is delimiter
* The code does not yet consider which form of the word it is when referring to other words, so a verb may point to a noun and not make sense (fix in progress).
