import { Global, Module } from '@nestjs/common';
import { PrismaService } from './prisma.service';

@Global() // optional, damit PrismaService überall verfügbar ist
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
