-- CreateTable
CREATE TABLE "aircraft_utilization" (
    "id" TEXT NOT NULL,
    "airline" TEXT,
    "month" TEXT,
    "msn" TEXT,
    "registration" TEXT,
    "aircraft_type" TEXT,
    "days_flown" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "aircraft_utilization_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_data" (
    "id" TEXT NOT NULL,
    "component_type" TEXT NOT NULL,
    "TSN" DOUBLE PRECISION,
    "CSN" INTEGER,
    "MonthlyUtil_Hrs" DOUBLE PRECISION,
    "MonthlyUtil_Cyc" INTEGER,
    "SerialNumber" TEXT,
    "location" TEXT,
    "aircraftId" TEXT NOT NULL,

    CONSTRAINT "component_data_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "aircraft_utilization_registration_month_idx" ON "aircraft_utilization"("registration", "month");

-- CreateIndex
CREATE INDEX "aircraft_utilization_msn_idx" ON "aircraft_utilization"("msn");

-- CreateIndex
CREATE INDEX "component_data_component_type_idx" ON "component_data"("component_type");

-- CreateIndex
CREATE INDEX "component_data_SerialNumber_idx" ON "component_data"("SerialNumber");

-- AddForeignKey
ALTER TABLE "component_data" ADD CONSTRAINT "component_data_aircraftId_fkey" FOREIGN KEY ("aircraftId") REFERENCES "aircraft_utilization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
