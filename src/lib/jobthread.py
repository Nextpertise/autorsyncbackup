import threading
import time

from lib.logger import logger

class jobThread (threading.Thread):
    def __init__(self, id, exitFlag, queueLock, director, q):
        threading.Thread.__init__(self)
        self.id = id
        self.exitFlag = exitFlag
        self.queueLock = queueLock
        self.director = director
        self.q = q
        
    def run(self):
        logger().debug("Starting thread: %d" % self.id)
        self.executeJob(self.q)
        logger().debug("Exiting thread: %d" % self.id)
        
    def executeJob(self, q):
        while not self.exitFlag.is_set():
            self.queueLock.acquire()
            if not q.empty():
                job = q.get()
                
                self.queueLock.release()
                logger().info("Start job for hostname: [%s] in queue: [%d]" % (job.hostname, self.id))
                self.director.checkBackupEnvironment(job)
                self.director.sanityCheckWorkingDirectory(job)
                latest = self.director.checkForPreviousBackup(job)
                self.director.executeRsync(job, latest)
                self.director.processBackupStatus(job)
                logger().info("Stop job for hostname: %s: [%d]" % (job.hostname, self.id))
            else:
                self.queueLock.release()
            time.sleep(1)
