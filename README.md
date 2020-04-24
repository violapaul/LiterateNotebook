# Literate Notebook

## Motivation

I've found the most productive way to write and document code is by building it up in a Jupyter notebook.  I use the notebook to define the problem, the inputs and outputs, include examples, references and links, and then build up to a final set of solutions.  Along the way I end up writing functions which are similar or identical to a set functions to be collected into a module (the python name for libraries of functions).  Modules are critical because they can be imported and used in other notebooks/modules.  

Unfortunately, the notebook and the module can get out of sync.  I'll find a bug in the module as I am using it, and then go fix it.  Or I'll add a bit of functionality.  Gradually the notebook becomes stale.  Most of the info in the notebook is still true, but it doesn't reflect the final details accurately.

It would be way better if the **Notebook was the Module** and the **Module was the Notebook**.  

The code in this notebook/module provides a means to unify these concepts.

## Background

This notion is clearly related to *Literate Programming* (LP).  Links:

- [Knuth's Paper](http://www.literateprogramming.com/knuthweb.pdf), great but not that accessible.
- [Literate Programming Site](http://www.literateprogramming.com/), oddly structured (what is this site trying to achieve?).
- [Wikipedia Page](https://en.wikipedia.org/wiki/Literate_programming), always a good place to start.
- [A Gentle Introduction](http://axiom-developer.org/axiom-website/litprog.html), one of the best I have read.
- [Physics Based Rendering](http://www.pbr-book.org/3ed-2018/contents.html), a great book which uses LP to teach and define a complete working system.

The "literate programming" idea is that code is a byproduct of the thinking and teaching process.  So rather than write a program with embedded comments, you write a teaching document in Knuth's WEB language which includes the code, using markup that allows you to later tease the two pieces apart into the code (Pascal in his example) and the document (TeX).  The final code itself is not meant for anyone to read... it is only intended for the compiler.  The surprising part for me is that the code is never really presented in one piece, though it could be.  In the WEB document it is sliced and diced into pieces and only assembled at the end (more on this below).  (BTW, Knuth is brilliant and always right, but I am not a huge fan of the look and feel of the languages he developed.  WEB was never widely used, and of course "web" now means something entirely different. TeX, while universal and awesome, has a programming language which kind of sucks.  The algorithms in his books were written in MIX, another painful choice. Python does not suck and neither do Jupyter notebooks.)

Jupyter notebooks are sort of similar to "literate programs" containing code and documentation side by side.  As they are currently used, notebooks are both better and worse.  They are better because a notebook can include examples,  running code, and code outputs.  A Notebook is not just a dead document.  Notebooks are worse because they are typically not used to create code libraries which are reusable by other modules and other users (this is the ultimate goal of most programming).

I am arguing for a **Literate Notebook**, a WYSIWYG document including running examples and results, which can be post-processed to create the module which can then be used by other python programs and notebooks.  

Doesn't it already work that way?  Unfortunately not.  The simplest (boring) reason is that a notebook is a JSON file and not a python module (the notebook extension is `.ipynb`).  This JSON includes markdown cells (like this one) and code cells.  At a minimum we would need to pull the code out of the ipynb file and put it into a `.py` file.  But a typical notebook also includes non-essential code: references to example data, or partially written functionality, or attempts to decompose the problem (like any textbook would).  This code is not welcome in our streamlined and efficient module (though it is super useful when understanding the module).

Note, jupyter notebooks already include a scheme for converting ipynb files into "python" (`juypyter nbconvert`).  But the conversion is hamfisted and the code not terribly reusable.  And it includes all the code, both the ephemera and the reusable functions.

My proposal is quite simple (all good ideas are simple, though not all simple ideas are good): add a few tags, harmlessly included in comments, which flag cells as "notebook only" or "destined for the module".  Using some discipline in the notebook authoring process, it is possible to extract the module from the literate notebook, and they magically stay in sync forever.  The fact that the notebook is straightforward JSON helps tremendously.

Why doesn't everyone do this?  Honestly not sure. The missing piece is actually quite simple.

Note, the extracted module, while it can stand on its own and will have embedded comments, should not be read/edited directly: *read and understand the code in the literate notebook.*  Over time it is possible folks will edit the module, disconnecting the module from the literate notebook.  At that point the literate notebook loses most of its value, and should be deleted.


### Literate Programming is a bit different

To be honest, LP can be mysterious, and WEB examples seem sort of complex. Central to WEB is a feature missing from the trivially simple Literate Notebook defined above:  *single functions can be decomposed into pieces and described independently.*  The final "tangling" process, takes these pieces and weaves them back together into a single syntactically valid function.  The  Pascal example from Knuth's original paper is a single tangled mess (hence the name tangle for the process of constructing the source code).  Below is the resulting Pascal (its unfair to judge this code too closely, since later tools do a much better job):

    {1:}{2:}PROGRAM PRINTPRIMES(OUTPUT);CONST M=1000;{5:}RR=50;CC=4;WW=10;{:5}{19:}ORDMAX=30;{:19}VAR{4:}P:ARRAY[1..M]OF INTEGER;{:4}{7:}PAGENUMBER:INTEGER;PAGEOFFSET:INTEGER;ROWOFFSET:INTEGER;C:0..CC;{:7}{12:}J:INTEGER;K:0..M;{:12}{15:}JPRIME:BOOLEAN;{:15}{17:}ORD:2..ORDMAX;SQUARE:INTEGER;{:17}{23:}N:2..ORDMAX;{:23}{24:}MULT:ARRAY[2..ORDMAX]OF INTEGER;{:24}BEGIN{3:}{11:}{16:}J:=1;K:=1;P[1]:=2;{:16}{18:}ORD:=2;SQUARE:=9;{:18};WHILE K<M DO BEGIN{14:}REPEAT J:=J+2;{20:}IF J=SQUARE THEN BEGIN ORD:=ORD+1;{21:}SQUARE:=P[ORD]*P[ORD];{:21}{25:}MULT[ORD-1]:=J;{:25};END{:20};{22:}N:=2;JPRIME:=TRUE;WHILE(N<ORD)AND JPRIME DO BEGIN{26:}WHILE MULT[N]<J DO MULT[N]:=MULT[N]+P[N]+P[N];IF MULT[N]=J THEN JPRIME:=FALSE{:26};N:=N+1;END{:22};UNTIL JPRIME{:14};K:=K+1;P[K]:=J;END{:11};{8:}BEGIN PAGENUMBER:=1;PAGEOFFSET:=1;WHILE PAGEOFFSET<=M DO BEGIN{9:}BEGIN WRITE(’The First ’);WRITE(M:1);WRITE(’ Prime Numbers --- Page ’);WRITE(PAGENUMBER:1);WRITELN;WRITELN;FOR ROWOFFSET:=PAGEOFFSET TO PAGEOFFSET+RR-1DO{10:}BEGIN FOR C:=0 TO CC-1 DO IF ROWOFFSET+C*RR<=M THEN WRITE(P[ROWOFFSET+C*RR]:WW);WRITELN;END{:10};PAGE;END{:9};PAGENUMBER:=PAGENUMBER+1;PAGEOFFSET:=PAGEOFFSET+RR*CC;END;END{:8}{:3};END.{:2}{:1}

I think the message is clear, don't look at the code.  If you did **have** to look at it the particular the bit between the pair of comments `{7:} ... {:7}` is *defined* and described in section 7 of the WEB document.

    {7:} PAGENUMBER:INTEGER;PAGEOFFSET:INTEGER;ROWOFFSET:INTEGER;C:0..CC;{:7}

Perhaps the simplest way to think of LP using WEB: 

- Code can be broken down into the tiny pieces.
- Rather than forcing the programmer to squeeze comments into the code itself, the comments **and the code** are defined and discussed elsewhere.
- The code can be defined and documented in any order.
- Everything is assembled at the end.  The document looks great.  The actual final code is left a bit mysterious.

I guess I write programs in a different way...  by writing programs. How would debugging of this final code work? Or how can I be sure this sliced and diced program even worked at all?  I often need to run code to see what I've missed.  Corner cases.  Missing steps.  One of the greatest things about programming is that the compiler/interpreter will find your bugs by failing to do what you intended.  I am not sure how that feedback loop works with WEB. And modern IDE's find a lot of issues very early (like missing references and syntax errors). 

I am proposing something simpler and less powerful, but more closely associated with typical programming.  Every modern programming language allows you to break computations into pieces through the use of functions.  Each function is syntactically separate and can be described independently.  I imagine Literate Notebooks using functions to decompose and document functionality.  I also believe you can build up functionality through partial or even failed attempts.  These can all go in the notebook and provide a scheme for understanding the final set of functions.

I am pretty sure I would **not** like programming in WEB.  Expressions interact in complex ways, mostly through variable definitions that are shared in the various namespaces of the function.  It can be further complex if the syntax of the language does not simply allow you to string together subpieces.  Using LP and WEB is likely easier in a language like lisp; since the syntax is trivial, the pieces can be easily glued back together.  Its even easier in a functional subset of lisp (like [Clojure](https://clojure.org/)), because then the subpieces only interact through the values of the expressions (no side effects).  LP for Clojure might work for me. 

I honestly got lost as Knuth wrote a Pascal function in WEB.  It was super hard to just see the whole structure of the function, and I was worried that it would not just glue back together in a meaningful way.  I kept asking, *can't I just see the function*?

**How would I fix it?**  Might as well jot this down.  

- Have the final function available at all times, nicely formatted (not tangled!).  Perhaps in a window at the side.
- Allow access to the associated documentation by hovering over the code.
- One click to run on test data.
- Allow editing of the code directly, and this updates the WEB doc.

I think this could work.  But I am not sure I'd love it.  I still write code by writing code.

