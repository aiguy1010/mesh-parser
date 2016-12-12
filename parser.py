from matplotlib import pyplot as plt
from os import listdir

class Frame:
    def __init__(self, timestamp, lines=[]):
        self.timestamp = timestamp
        self.lines = lines

        # Pull out connection quality numbers
        self.qualities = []
        for line in self.lines:
            opParInd = line.find('(')
            self.qualities.append( int(line[opParInd+1:opParInd+3]) )

        # Calculate average quality
        self.meanQuality = sum(self.qualities)/len(self.qualities)


class MeshDataLog:
    def __init__(self, filename):
        # Pull in the frames
        self.frames = []
        self.__load__(filename)

        # Calc average quality
        self.meanQuality = sum(map(lambda x:x.meanQuality, self.frames)) / len(self.frames)


    def __load__(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        l=0
        frameLines = []
        while l < len(lines):
            if lines[l].strip() != '':
                frameLines.append( lines[l].strip() )
                l += 1
            else:
                timestamp = lines[l+5].strip()
                self.frames.append( Frame(timestamp, frameLines) )
                l += 7

def graphFolder(path, title='',ax=None):
    filenames = listdir(path)

    IQpairs = [] # Interval Quality pairs

    floodMean = 0
    for filename in filenames:
        # Load the file and get the mean quality
        dataLog = MeshDataLog(path+'/'+filename)

        # Get the ping interval
        endOfTime = filename.find('s')
        tPrefix = filename[:endOfTime]

        # If this is the flood interval, treat it differently
        if tPrefix == 'f':
            floodMean = dataLog.meanQuality
        else:
            IQpairs.append( (float(tPrefix), dataLog.meanQuality) )

    # Make sure data points are orded by interval length
    IQpairs.sort( key=lambda x:x[0] )
    Is, Qs = zip( *IQpairs ) # <-- Python Zoodoo!

    # Graph it
    if ax:
        plt.axes(ax)
    plt.xlabel('Ping Interval (seconds)')
    plt.ylabel('Batman Link Quality (0-255)')
    plt.ylim([0,20])
    plt.title(title)
    tLine, = plt.plot(Is, Qs, linestyle='--', color='b', marker='o', label='Quality/Interval')
    fLine, = plt.plot([0,1], [floodMean, floodMean], linestyle=':', color='r', label='Quality at Flood')
    plt.legend(handles=[tLine, fLine])


if __name__ == '__main__':
    f, (ax1, ax2) = plt.subplots(1,2) # One row, two columns
    graphFolder('16node1chan/sshpingRouter', 'Pinging Router', ax1)
    graphFolder('16node1chan/sshpingBcast', 'Pinging Broadcast', ax2)
    plt.show()
