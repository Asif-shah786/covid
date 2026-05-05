SELECT * FROM CovidDeaths
Order By 3, 4;

SELECT date, CovidVaccinations.new_vaccinations FROM CovidVaccinations
Order by  new_vaccinations DESC;



SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'CovidDeaths'
ORDER BY ORDINAL_POSITION;

SELECT * FROM CovidDeaths
Order By 3, 4;


-- Select data that we are going to be using
SELECT location, date , total_cases, new_cases, total_deaths, population from CovidDeaths
ORDER BY 1, 2;

-- Looking at total_cases vs total_deaths
SELECT location, date , total_cases, total_deaths, (total_deaths/total_cases)*100 AS DeathPercentage from CovidDeaths
ORDER BY 1, 2;

-- Looking at total_cases vs total_deaths
-- shows likelihood of dying if you contract Covid in my country
SELECT location, date , total_cases, total_deaths, (total_deaths/total_cases)*100 AS PakistanDeathPercentage
from CovidDeaths
WHERE location LIKE '%pak%'
ORDER BY 1, 2;


-- Looking at Cases vs Population
-- shows what percentage of population got Covid Pakistan
SELECT location, date , population, total_cases, (total_cases/population)*100 AS PopulationInfected
from CovidDeaths
WHERE location LIKE '%pak%'
ORDER BY 1, 2;

-- Looking at countries with highest infection rate compared to population

SELECT location , population, MAX(total_cases) as HighestInfectionCount, MAX((total_cases/population))*100 AS PercentPopulationInfected
from CovidDeaths
# WHERE location LIKE '%pak%'
GROUP BY location, population
ORDER BY PercentPopulationInfected desc;


-- Looking at countries with highest Death Count per population

SELECT location , Max(total_deaths) AS TotalDeathCount
from CovidDeaths
# WHERE location LIKE '%pak%'
Where continent is NOT NULL
GROUP BY location
ORDER BY TotalDeathCount desc;


-- Breaking things down by Continent
-- showing continent with highest death count per population

SELECT continent , Max(total_deaths) AS TotalDeathCount
from CovidDeaths
Where continent is NOT NULL
GROUP BY continent
ORDER BY TotalDeathCount desc;

-- Global Numbers

-- Total Global death percentage

SELECT SUM(CovidDeaths.new_cases) as total_cases, SUM(CovidDeaths.new_deaths) as total_deaths,
       (SUM(CovidDeaths.new_deaths)/ SUM(CovidDeaths.new_cases)) * 100 as GlobalDeathPercentageByDay
FROM CovidDeaths
Where continent is NOT NULL;

-- Global Death percentage per day
SELECT date, SUM(CovidDeaths.new_cases) as total_cases, SUM(CovidDeaths.new_deaths) as total_deaths,
       (SUM(CovidDeaths.new_deaths)/ SUM(CovidDeaths.new_cases)) * 100 as GlobalDeathPercentageByDay
FROM CovidDeaths
Where continent is NOT NULL
GROUP BY date
ORDER BY 1, 2;


-- Joining tables

Select *
FROM CovidDeaths cd
    join CovidVaccinations cv on cd.location = cv.location
AND cd.date = cv.date
WHERE cd.continent is NOT NULL;

-- Looking at Total population vs Vaccinations

-- Using CTE

-- Because for following if we want to use "RollingPeopleVaccinated" in SELECT statement we cannot do that

WITH Popvsvac (Continent, Location, Date, Population, New_Vaccination, RollingPeopleVaccinated)
    as (
        Select cd.continent, cd.location, cd.date, cd.population, cv.new_vaccinations, SUM(cd.new_vaccinations) OVER (PARTITION BY cd.location ORDER BY cd.location, cd.date) as RollingPeopleVaccinated
FROM CovidDeaths cd
    join CovidVaccinations cv on cd.location = cv.location
    AND cd.date = cv.date
WHERE cd.continent is NOT NULL
    )

Select *, (RollingPeopleVaccinated/Population)*100
FROM Popvsvac;



-- TEMP TABLE
DROP TABLE IF EXISTS PercentagePopulationVaccinated;
CREATE TEMPORARY TABLE PercentagePopulationVaccinated (
    Continent VARCHAR(255),
    Location VARCHAR(255),
    Date DATE,
    Population BIGINT,
    New_vaccinations BIGINT,
    RollingPeopleVaccinated BIGINT
);

INSERT INTO PercentagePopulationVaccinated
SELECT
    cd.continent,
    cd.location,
    cd.date,
    cd.population,
    cv.new_vaccinations,
    SUM(cv.new_vaccinations) OVER (
        PARTITION BY cd.location
        ORDER BY cd.date
    ) AS RollingPeopleVaccinated
FROM CovidDeaths cd
JOIN CovidVaccinations cv
    ON cd.location = cv.location
   AND cd.date = cv.date
WHERE cd.continent IS NOT NULL;

SELECT *,
       (RollingPeopleVaccinated / Population) * 100 AS VaccinationPercentage
FROM PercentagePopulationVaccinated;


-- Creating view to store data for later visualization

CREATE VIEW PercentPopulationVaccinated as
    SELECT
    cd.continent,
    cd.location,
    cd.date,
    cd.population,
    cv.new_vaccinations,
    SUM(cv.new_vaccinations) OVER (
        PARTITION BY cd.location
        ORDER BY cd.date
    ) AS RollingPeopleVaccinated
FROM CovidDeaths cd
JOIN CovidVaccinations cv
    ON cd.location = cv.location
   AND cd.date = cv.date
WHERE cd.continent IS NOT NULL;


SELECT *
FROM PercentPopulationVaccinated;