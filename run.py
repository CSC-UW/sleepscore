import sleepscore

binPath = ""
datatype = 'SGLX'
downSample = 100.0  # (Hz)
tStart = None  # 0 (s)
# tEnd = None
tEnd = 60.0  # (s)
# chanList = None  # All saved
chanList = [0]
chanListType = 'indices'  # chanList interpreted as indices of saved channels
chanLabelsMap = None  # Map channel relabelling (keys are values in `chanList`)
unit = 'uV'
kwargs_sleep = {
    'downsample': None,
}


sleepscore.load_and_score(
    binPath,
    datatype=datatype,
    downSample=downSample,
    tStart=tStart,
    tEnd=tEnd,
    chanList=chanList,
    chanListType=chanListType,
    chanLabelsMap=chanLabelsMap,
    unit=unit,
    kwargs_sleep=kwargs_sleep,
)
