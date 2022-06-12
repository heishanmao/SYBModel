#  A Gurobi Model

## SYBModel_V13.py

non-convex  failed  unbounded
## log
C:\Users\heish\anaconda3\envs\gurobi\python.exe "C:\Program Files\JetBrains\PyCharm 2019.3.4\plugins\python\helpers\pydev\pydevd.py" --cmd-line --multiprocess --qt-support=auto --client 127.0.0.1 --port 54620 --file "D:/OneDrive - University of Tennessee/Scripts/SYBModel/SYBModel_V18.py"
Connected to pydev debugger (build 221.5787.24)
 Model Name: SSP2_2030
Country Elevators: 227
Stream Elevators: 10
Rail Elevators: 6
Exports: 8
Imports: 2
Set parameter Username
Academic license - for non-commercial use only - expires 2022-08-01
Set parameter NumericFocus to value 3
Set parameter NonConvex to value 2
Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (win64)
Thread count: 8 physical cores, 8 logical processors, using up to 8 threads
Optimize a model with 706 rows, 5368 columns and 10276 nonzeros
Model fingerprint: 0x701b8a05
Model has 227 quadratic objective terms
Model has 1 quadratic constraint
Coefficient statistics:
  Matrix range     [1e+00, 5e+07]
  QMatrix range    [1e+00, 1e+00]
  QLMatrix range   [5e+00, 5e+00]
  Objective range  [1e+00, 2e+07]
  QObjective range [2e+00, 2e+00]
  Bounds range     [1e+00, 1e+00]
  RHS range        [1e+00, 3e+09]
  QRHS range       [3e+02, 3e+02]
Warning: Model contains large rhs
Presolve removed 8 rows and 130 columns

Continuous model is non-convex -- solving as a MIP

Presolve removed 251 rows and 373 columns
Presolve time: 0.01s
Presolved: 1819 rows, 5451 columns, 16345 nonzeros
Presolved model has 454 bilinear constraint(s)
Variable types: 5451 continuous, 0 integer (0 binary)

Root relaxation: unbounded, 895 iterations, 0.03 seconds (0.03 work units)

    Nodes    |    Current Node    |     Objective Bounds      |     Work
 Expl Unexpl |  Obj  Depth IntInf | Incumbent    BestBd   Gap | It/Node Time

     0     0  postponed    0               -          -      -     -    0s
Exploring 100 nodes in MinRel heuristic
Model proven infeasible by MinRel heuristic
     0     2  postponed    0               -          -      -     -    0s
*    8    10               3    4.782293e+17          -      -  1331    1s
*   18    14               4    4.782308e+17          -      -   727    1s
*   23    14               5    4.786070e+17          -      -   632    1s
*   24    14               5    4.793697e+17          -      -   612    1s
*   38     8               6    4.808958e+17          -      -   438    1s
*   41     8               7    4.900326e+17          -      -   421    1s
*   49     4               8    4.920207e+17          -      -   375    1s
*   66     8              11    5.061910e+17          -      -   345    1s
*   83    12              12    5.345318e+17          -      -   346    1s
*  108    10              14    5.912132e+17          -      -   340    2s
*  134    12              17    7.045761e+17          -      -   318    2s
*  148    10              18    9.313019e+17          -      -   334    2s
*  170    10              19    9.313019e+17          -      -   334    2s
*  184    18              20    1.384753e+18          -      -   328    2s
*  209    15              23    2.291657e+18          -      -   311    2s
*  226    10              24    4.105463e+18          -      -   301    2s
*  257    14              26    6.715113e+18          -      -   299    3s
*  290    41              26    7.733076e+18          -      -   290    3s
*  352    62              38    1.295244e+19          -      -   259    3s
*  369    62              28    1.498830e+19          -      -   256    3s
*  436    96              30    2.949875e+19          -      -   251    4s
*  485   113              32    5.851965e+19          -      -   243    4s
   527   151 3.1198e+20   26  206 5.8520e+19          -      -   234    5s
*  543   151              34    1.002753e+20          -      -   240    5s
*  597   151              40    2.326451e+20          -      -   227    5s
*  599   151              41    4.648123e+20          -      -   228    5s
*  705   202              42    9.291467e+20          -      -   227    5s
*  707   202              43    1.857816e+21          -      -   228    5s
*  870   266              55    3.715153e+21          -      -   239    6s
*  942   415              87    7.429829e+21          -      -   232    7s
  1149   757  postponed  141      7.4298e+21          -      -   234   10s
* 1242   757              93    1.485918e+22          -      -   219   10s
* 1485   757             105    2.971788e+22          -      -   210   10s

Explored 1561 nodes (338059 simplex iterations) in 10.21 seconds (9.07 work units)
Thread count was 8 (of 8 available processors)

Solution count 10: 2.97179e+22 1.48592e+22 7.42983e+21 ... 5.85197e+19

Model is unbounded
Warning: max constraint violation (1.9073e-05) exceeds tolerance
Best objective 2.971788142874e+22, best bound -, gap -
 Model failed 
Python 3.8.12 (default, Oct 12 2021, 03:01:40) [MSC v.1916 64 bit (AMD64)]
Type 'copyright', 'credits' or 'license' for more information
IPython 7.29.0 -- An enhanced Interactive Python. Type '?' for help.
PyDev console: using IPython 7.29.0

Python 3.8.12 (default, Oct 12 2021, 03:01:40) [MSC v.1916 64 bit (AMD64)] on win32
forrtl: error (200): program aborting due to control-C event
Image              PC                Routine            Line        Source             
libifcoremd.dll    00007FFEA7213B58  Unknown               Unknown  Unknown
KERNELBASE.dll     00007FFF042359E5  Unknown               Unknown  Unknown
KERNEL32.DLL       00007FFF066B54E0  Unknown               Unknown  Unknown
ntdll.dll          00007FFF068E485B  Unknown               Unknown  Unknown

Process finished with exit code 0
