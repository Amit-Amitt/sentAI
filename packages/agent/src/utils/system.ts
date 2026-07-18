import * as os from 'os';

let lastCpuTime = process.cpuUsage();
let lastHrTime = process.hrtime();

export function getSystemStats() {
  // Calculate CPU percentage
  const currentCpuTime = process.cpuUsage();
  const currentHrTime = process.hrtime();

  const userDiff = currentCpuTime.user - lastCpuTime.user;
  const sysDiff = currentCpuTime.system - lastCpuTime.system;
  
  const timeDiff = (currentHrTime[0] - lastHrTime[0]) * 1e6 + (currentHrTime[1] - lastHrTime[1]) / 1e3;
  
  const cpuPercent = timeDiff > 0 ? ((userDiff + sysDiff) / timeDiff) * 100 : 0;

  lastCpuTime = currentCpuTime;
  lastHrTime = currentHrTime;

  const memoryUsage = process.memoryUsage();
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const memPercent = ((totalMem - freeMem) / totalMem) * 100;

  return {
    cpuPercent: Math.min(Math.max(cpuPercent, 0), 100),
    memoryPercent: Math.min(Math.max(memPercent, 0), 100),
    heapUsed: memoryUsage.heapUsed,
    heapTotal: memoryUsage.heapTotal,
    uptime: process.uptime()
  };
}
