import { Controller, Get } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Controller('jobs')
export class JobsController {
  constructor(private prisma: PrismaService) {}

  @Get()
  async getJobs() {
    return this.prisma.job.findMany({
      select: {
        id: true,
        title: true,
        description: true,
        startDate: true,
        endDate: true,
        status: true,
      },
    });
  }
}
