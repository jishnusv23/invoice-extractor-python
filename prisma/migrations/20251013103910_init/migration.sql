-- CreateTable
CREATE TABLE "lessees" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "month" TEXT NOT NULL,
    "fileName" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "lessees_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "assets" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "serialNumber" TEXT NOT NULL,
    "registrationNumber" TEXT NOT NULL,
    "validation_status" TEXT NOT NULL,
    "report_status" TEXT NOT NULL,
    "obligation_status" TEXT NOT NULL,
    "month" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lesseeId" TEXT NOT NULL,

    CONSTRAINT "assets_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "components" (
    "id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "serialNumber" TEXT NOT NULL,
    "lastUtilizationDate" TEXT NOT NULL,
    "flightHours" TEXT NOT NULL,
    "flightCycles" TEXT NOT NULL,
    "apuHours" TEXT NOT NULL,
    "apuCycles" TEXT NOT NULL,
    "tsnAtPeriod" TEXT NOT NULL,
    "csnAtPeriod" TEXT NOT NULL,
    "tsnAtPeriodEnd" TEXT NOT NULL,
    "csnAtPeriodEnd" TEXT NOT NULL,
    "lastTsnCsnUpdate" TEXT NOT NULL,
    "lastTsnUtilization" TEXT NOT NULL,
    "lastCsnUtilization" TEXT NOT NULL,
    "attachmentStatus" TEXT NOT NULL,
    "engineThrust" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "utilReportStatus" TEXT NOT NULL,
    "asset_status" TEXT NOT NULL,
    "derate" TEXT NOT NULL,
    "month" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "assetId" TEXT NOT NULL,

    CONSTRAINT "components_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "lessees_name_key" ON "lessees"("name");

-- CreateIndex
CREATE UNIQUE INDEX "lessees_name_month_key" ON "lessees"("name", "month");

-- AddForeignKey
ALTER TABLE "assets" ADD CONSTRAINT "assets_lesseeId_fkey" FOREIGN KEY ("lesseeId") REFERENCES "lessees"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "components" ADD CONSTRAINT "components_assetId_fkey" FOREIGN KEY ("assetId") REFERENCES "assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;
