# R13: fixed-cohort estimand

Disposition: **addressed**. Main and supplement retain the descriptive8/12 fraction and0/3,2/3,3/3,3/3 task counts, but remove the Wilson95% interval. They explicitly assert no exchangeable Bernoulli or future-task sampling model. This avoids assigning coverage to an unspecified target rather than hiding task clustering behind a “descriptive interval” label.

The new cohort-description replay checks twelve distinct IDs and four tasks with three sessions each directly from the unchanged primary records. Its artifact states the population and observed fraction and leaves confidence_interval null. Historical lock/analysis outputs containing the former interval remain historical artifacts; they are not silently rewritten.

The20-check preservation/reporting regression and clean13/5/18 page builds pass. No larger capability study, model comparison or new provider call is implied.
