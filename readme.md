# understudy

Understudy is a web app that allows for looking up UCF course codes and getting information about professors who teach (or have taught) the class; comparing their statistics, grade distrubutions and reviews; and generating meaningful points of comparison to help you make an informed decision.


## why?
Because, as far as I can tell, this kind of service isn't really available. The best we can do is rely on word of mouth (or the occasional search result for a professors name in `r/UCF`), as well as whatever information RateMyProfessor provides.

The issue is none of this data is very accessible, and it's not presented in a way that's very useful (i.e. RateMyProfessor doesn't allow lookup and comparison from a course code, beyond independent data on a single professor's section).

That's what understudy aims to provide: an accessible platform that puts all this data in one place and presents it in a useful way, to help students make informed decisions and get the best education we can.


## the tech

Understudy has two components; there's a service that periodically fetches available data from RateMyProfessor, Reddit, etc., collating information about UCF courses/professors, processing and storing the results in a Mongo database.

The second component is what the end user sees; a Streamlit web app that compiles the data we've prefetched from the server and sends relevant details through an inference chain to generate comparisons and other useful information.


## things I'd like to make it do

- Better data utilization: I've got quite a bit of data I didn't have time to really utilize to the fullest extent. For example I have helpful/unhelpful votes on ratings which could be part of some heuristic for weighting reviews.
