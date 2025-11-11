import { Module } from '@nestjs/common';
import { JobsController } from './jobs.controller';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [PrismaModule],
  controllers: [JobsController],
})
export class JobsModule {}
