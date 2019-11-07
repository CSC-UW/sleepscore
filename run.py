import sleepscore

binPath = ""
datatype = 'SGLX'
downSample = 100.0 # (Hz)
tStart = None # 0 (s)
# tEnd = None
tEnd = 60.0  # (s)
# chanList = None  # All saved
chanList = [0]
chanListType = 'indices' # chanList interpreted as indices of saved channels
unit = 'uV'
kwargs_sleep = {}

sleepscore.load_and_score(
    binPath, 
    datatype=datatype,
    downSample=downSample,
    tStart=tStart,
    tEnd=tEnd,
    chanList=chanList,
    chanListType=chanListType,
    unit=unit,
    kwargs_sleep=kwargs_sleep,
)
