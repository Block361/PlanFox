import { Controller, Get, Post, Body } from '@nestjs/common';
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

  @Post()
  async createJob(
    @Body()
    data: {
      title: string;
      startDate: string;
      endDate: string;
      description?: string;
      userId: number; // ← User-ID vom Frontend mitgeben
    },
  ) {
    return this.prisma.job.create({
      data: {
        title: data.title,
        startDate: new Date(data.startDate),
        endDate: new Date(data.endDate),
        description: data.description ?? '',
        status: 'open',
        user: {
          connect: { id: data.userId }, // ← bestehender Benutzer wird verknüpft
        },
      },
    });
  }
}
