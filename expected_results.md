# ArtiFinder USENIX 2026 Reproduction Results

## Section 1: Introduction

Artifact presence over the years:
2000: 1.23%
2025: 72.33%

## Section 3.1: ArtiFinder Design


## Section 3.2: ArtiFinder Accuracy

Accuracy for SecArtifacts dataset: (n=879)
  Correct presence: 87.0% (exact: 58.6%, alt: 28.4%)
  Correct absence: 8.5%, (no link: 0.0%, missing link: 8.5%)
  Wrong presence: 2.2%, (no link: 0.0%, incorrect link: 2.2%)
  Wrong absence: 2.3%
  Overall accuracy: 95.6%
Accuracy for GetIn dataset: (n=742)
  Correct presence: 39.1% (exact: 31.8%, alt: 7.3%)
  Correct absence: 54.2%, (no link: 45.8%, missing link: 8.4%)
  Wrong presence: 4.4%, (no link: 4.4%, incorrect link: 0.0%)
  Wrong absence: 2.3%
  Overall accuracy: 93.3%
Accuracy for Manual Sample dataset: (n=84)
  Correct presence: 6.0% (exact: 6.0%, alt: 0.0%)
  Correct absence: 92.9%, (no link: 92.9%, missing link: 0.0%)
  Wrong presence: 1.2%, (no link: 1.2%, incorrect link: 0.0%)
  Wrong absence: 0.0%
  Overall accuracy: 98.8%

## Section 3.3: Ablation Study

Ablation study for heuristic: LocationInPaper
Filtered 643 occurrences of heuristic LocationInPaper
percentage of links affected: 81.6%
SecArtifacts accuracy without LocationInPaper: 88.83%
-----
Ablation study for heuristic: GithubRepo
Filtered 407 occurrences of heuristic GithubRepo
percentage of links affected: 51.65%
SecArtifacts accuracy without GithubRepo: 83.63%
-----

## Section 4.1: Artifact Presence

Observed Difference: 0.3779
P-Value: True
Result: Reject H0

## Section 4.2: Artifact Badges


## Section 4.3: Artifact Platforms

Papers using Zenodo in 2025: 49.44%
Papers using GitHub in 2025: 59.59%
Domains using .org TLD: 42.15%
Domains using .com TLD: 22.31%
Domains using .net TLD: 9.92%
Total artifacts on dedicated domains: 121

## Section 4.4: Artifact Availability

Percentage of GitHub artifacts without content: 2.57%

## Section 4.5: Artifact Topics

| Topic               |   With Artifact |   Without Artifact |   Total Papers | Artifact %   |
|---------------------|-----------------|--------------------|----------------|--------------|
| fuzzing             |             131 |                 47 |            178 | 73.60%       |
| microarchitectures  |              84 |                 35 |            119 | 70.59%       |
| vulnerabilities     |             200 |                147 |            347 | 57.64%       |
| hardware            |              94 |                 78 |            172 | 54.65%       |
| machine learning    |             311 |                296 |            607 | 51.24%       |
| privacy             |             418 |                424 |            842 | 49.64%       |
| malware             |              81 |                 84 |            165 | 49.09%       |
| browser security    |              68 |                 72 |            140 | 48.57%       |
| networking          |              48 |                 53 |            101 | 47.52%       |
| social issues       |              60 |                 67 |            127 | 47.24%       |
| intrusion detection |              51 |                 60 |            111 | 45.95%       |
| cryptocurrencies    |              95 |                114 |            209 | 45.45%       |
| computations        |              70 |                 85 |            155 | 45.16%       |
| mobile              |             125 |                194 |            319 | 39.18%       |
| encryption          |              44 |                 69 |            113 | 38.94%       |
| cryptographic       |             588 |               1090 |           1678 | 35.04%       |
| authentication      |              35 |                108 |            143 | 24.48%       |
| enforcing           |              89 |                293 |            382 | 23.30%       |
| cybersecurity       |              33 |                120 |            153 | 21.57%       |

## Section 4.6: Artifact Authors

Point-biserial correlation: 0.15, p-value: 2.2302896222250155e-48

Affiliation Artifact Release Ratios:
| Affiliation                                                             | Artifact %   |   Total Papers |   Artifacts |
|-------------------------------------------------------------------------|--------------|----------------|-------------|
| CISPA - Helmholtz Center for Information Security                       | 69.34%       |            274 |         190 |
| Technische Universitat Graz                                             | 66.67%       |             69 |          46 |
| Singapore Management University                                         | 66.07%       |             56 |          37 |
| Virginia Polytechnic Institute and State University                     | 65.15%       |             66 |          43 |
| Nanyang Technological University                                        | 64.38%       |             73 |          47 |
| Zhongguancun Laboratory                                                 | 63.64%       |             77 |          49 |
| Zhejiang University                                                     | 63.01%       |            219 |         138 |
| Huazhong University of Science and Technology                           | 62.50%       |             56 |          35 |
| Hong Kong University of Science and Technology                          | 62.22%       |             90 |          56 |
| The Hong Kong Polytechnic University                                    | 61.73%       |             81 |          50 |
| Vrije Universiteit Amsterdam                                            | 61.54%       |             78 |          48 |
| Fudan University                                                        | 60.95%       |            105 |          64 |
| Beijing National Research Center for Information Science and Technology | 60.78%       |             51 |          31 |
| Ant group                                                               | 60.38%       |             53 |          32 |
| Commonwealth Scientific and Industrial Research Organisation            | 60.00%       |             60 |          36 |
| University of Waterloo                                                  | 59.57%       |             94 |          56 |
| University of Virginia                                                  | 59.26%       |             81 |          48 |
| Tsinghua University                                                     | 57.85%       |            261 |         151 |
| University of California, Irvine                                        | 57.73%       |             97 |          56 |
| École Polytechnique Fédérale de Lausanne                                | 57.63%       |             59 |          34 |
| KU Leuven                                                               | 57.27%       |            110 |          63 |
| Wuhan University                                                        | 56.36%       |             55 |          31 |
| Ruhr-Universitat Bochum                                                 | 56.31%       |            206 |         116 |
| National University of Singapore                                        | 55.74%       |            122 |          68 |
| Korea Advanced Institute of Science and Technology                      | 55.56%       |             81 |          45 |
| New York University                                                     | 55.29%       |             85 |          47 |
| Shanghai Jiao Tong University                                           | 54.64%       |             97 |          53 |
| Pennsylvania State University                                           | 53.26%       |            184 |          98 |
| University of Massachusetts Amherst                                     | 53.12%       |             64 |          34 |
| Purdue University                                                       | 52.80%       |            286 |         151 |
| University of Chinese Academy of Sciences                               | 52.54%       |            118 |          62 |
|                                                                         | 52.41%       |            456 |         239 |
| Institute of Information Engineering                                    | 50.46%       |            109 |          55 |
| ETH Zürich                                                              | 50.39%       |            256 |         129 |
| Delft University of Technology                                          | 50.00%       |             72 |          36 |
| Johns Hopkins University                                                | 49.00%       |            100 |          49 |
| University of California, Riverside                                     | 48.91%       |             92 |          45 |
| University of Wisconsin-Madison                                         | 48.68%       |             76 |          37 |
| Chinese University of Hong Kong                                         | 46.88%       |             64 |          30 |
| Arizona State University                                                | 46.51%       |             86 |          40 |
| Seoul National University                                               | 46.15%       |             52 |          24 |
| NC State University                                                     | 45.90%       |             61 |          28 |
| University of Florida                                                   | 45.31%       |             64 |          29 |
| Northeastern University                                                 | 45.14%       |            144 |          65 |
| Tel Aviv University                                                     | 45.00%       |             60 |          27 |
| University of Minnesota Twin Cities                                     | 44.26%       |             61 |          27 |
| The George Washington University                                        | 44.00%       |             50 |          22 |
| TU Wien                                                                 | 43.48%       |             69 |          30 |
| Massachusetts Institute of Technology                                   | 43.48%       |             69 |          30 |
| Stanford University                                                     | 43.18%       |            132 |          57 |
| George Mason University                                                 | 43.18%       |             88 |          38 |
| Boston University                                                       | 41.86%       |             86 |          36 |
| Duke University                                                         | 41.86%       |             86 |          36 |
| Stony Brook University                                                  | 41.74%       |            115 |          48 |
| The Ohio State University                                               | 41.67%       |             84 |          35 |
| Georgia Institute of Technology                                         | 41.63%       |            257 |         107 |
| IMDEA Software Institute                                                | 41.18%       |            102 |          42 |
| Peking University                                                       | 41.18%       |             68 |          28 |
| Cornell Tech                                                            | 40.38%       |            104 |          42 |
| Princeton University                                                    | 40.00%       |            105 |          42 |
| University of Illinois Urbana-Champaign                                 | 39.90%       |            203 |          81 |
| Technische Universität Darmstadt                                        | 38.99%       |            159 |          62 |
| Northwestern University                                                 | 38.60%       |             57 |          22 |
| The University of Texas at Austin                                       | 38.36%       |             73 |          28 |
| The University of Chicago                                               | 37.93%       |             58 |          22 |
| University of Michigan, Ann Arbor                                       | 37.87%       |            169 |          64 |
| University of Maryland, College Park                                    | 37.77%       |            188 |          71 |
| Cornell University                                                      | 37.11%       |             97 |          36 |
| University of California, San Diego                                     | 36.17%       |            141 |          51 |
| Columbia University                                                     | 35.96%       |             89 |          32 |
| The University of Texas at Dallas                                       | 35.71%       |             56 |          20 |
| EURECOM                                                                 | 35.14%       |             74 |          26 |
| Indiana University Bloomington                                          | 34.59%       |            159 |          55 |
| University of Washington                                                | 33.78%       |             74 |          25 |
| University of Pennsylvania                                              | 33.33%       |             60 |          20 |
| Google LLC                                                              | 33.10%       |            145 |          48 |
| Carnegie Mellon University                                              | 32.82%       |            262 |          86 |
| MIT Computer Science & Artificial Intelligence Laboratory               | 32.73%       |             55 |          18 |
| Bar-Ilan University                                                     | 32.14%       |             56 |          18 |
| University of California, Berkeley                                      | 31.58%       |            266 |          84 |
| University of California, Santa Barbara                                 | 31.40%       |            121 |          38 |
| Universität des Saarlandes                                              | 31.18%       |             93 |          29 |
| Texas A&M University                                                    | 30.30%       |             66 |          20 |
| University of Illinois at Chicago                                       | 29.82%       |             57 |          17 |
| University College London                                               | 28.77%       |             73 |          21 |
| Microsoft Research                                                      | 28.33%       |            240 |          68 |
| Department of Computer Science                                          | 14.75%       |            122 |          18 |
| College of Computing                                                    | 10.53%       |             57 |           6 |
| College of Engineering                                                  | 10.00%       |             60 |           6 |
| IBM Thomas J. Watson Research Center                                    | 8.00%        |             50 |           4 |

## Section 4.7: Other Impacts

8216 papers with citation data
Raw point-biserial correlation: -0.103 (p=5.75e-21)
                            OLS Regression Results                            
==============================================================================
Dep. Variable:              citations   R-squared:                       0.069
Model:                            OLS   Adj. R-squared:                  0.068
Method:                 Least Squares   F-statistic:                     302.0
Date:                Thu, 18 Jun 2026   Prob (F-statistic):          2.71e-127
Time:                        13:25:25   Log-Likelihood:                -55808.
No. Observations:                8216   AIC:                         1.116e+05
Df Residuals:                    8213   BIC:                         1.116e+05
Df Model:                           2                                         
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        256.0147      7.570     33.822      0.000     241.177     270.853
artifact       4.8926      5.322      0.919      0.358      -5.540      15.325
year          -9.6009      0.425    -22.579      0.000     -10.434      -8.767
==============================================================================
Omnibus:                    15855.745   Durbin-Watson:                   1.904
Prob(Omnibus):                  0.000   Jarque-Bera (JB):         46319455.585
Skew:                          14.971   Prob(JB):                         0.00
Kurtosis:                     369.618   Cond. No.                         62.8
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
Raw point-biserial correlation: -0.147 (p=2.04e-10)
                            OLS Regression Results                            
==============================================================================
Dep. Variable:              citations   R-squared:                       0.161
Model:                            OLS   Adj. R-squared:                  0.160
Method:                 Least Squares   F-statistic:                     176.5
Date:                Thu, 18 Jun 2026   Prob (F-statistic):           7.91e-71
Time:                        13:25:25   Log-Likelihood:                -10046.
No. Observations:                1842   AIC:                         2.010e+04
Df Residuals:                    1839   BIC:                         2.012e+04
Df Model:                           2                                         
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        389.8720     20.440     19.074      0.000     349.784     429.960
artifact       1.2716      2.911      0.437      0.662      -4.437       6.980
year         -15.8033      0.905    -17.472      0.000     -17.577     -14.029
==============================================================================
Omnibus:                     3767.099   Durbin-Watson:                   1.619
Prob(Omnibus):                  0.000   Jarque-Bera (JB):         11489748.122
Skew:                          16.444   Prob(JB):                         0.00
Kurtosis:                     388.515   Cond. No.                         359.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

## Section 5: Case Study

Accuracy for ACSAC SecArtifacts dataset: (n=269)
  Correct presence: 67.7% (exact: 51.7%, alt: 16.0%)
  Correct absence: 21.9%, (no link: 0.0%, missing link: 21.9%)
  Wrong presence: 5.2%, (no link: 0.0%, incorrect link: 5.2%)
  Wrong absence: 5.2%
  Overall accuracy: 89.6%

