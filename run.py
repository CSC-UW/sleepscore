import sleepscore

binPath = ""
datatype = 'SGLX'
downSample = 100.0
tStart = None
tEnd = None
chanList = None
chanListType = 'indices'
unit = 'uV'
kwargs_sleep = {}

sleepscore.load_and_score(
    binPath, 
    datatype=datatype,
    downSample=downSample,
    tStart=tStart,
    tEnd=tEnd,
    chanList=None,
    chanListType=chanListType,
    unit=unit,
    kwargs_sleep=kwargs_sleep,
)
