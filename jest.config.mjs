export default {
    preset: 'ts-jest',
    testEnvironment: 'node',
    setupFiles: ['<rootDir>/tests/jest.setup.ts'],
    testMatch: ['**/tests/**/*.test.ts'],
    moduleNameMapper: {
      '^(\\.{1,2}/.*)\\.js$': '$1',
    },
    transform: {
      '^.+\\.tsx?$': ['ts-jest',{
          tsconfig: 'tsconfig.json',
        },
      ],
    },
  };