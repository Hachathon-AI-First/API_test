import js from "@eslint/js";
import globals from "globals";
import tseslint from "@typescript-eslint/eslint-plugin";
import parser from "@typescript-eslint/parser";

export default [
  {
    files: ["**/*.ts"],
    ignores: ["dist/**"],

    languageOptions: {
      parser,
      parserOptions: {
        sourceType: "module",
        ecmaVersion: "latest",
      },
      globals: {
        ...globals.node,
      },
    },

    plugins: {
      "@typescript-eslint": tseslint,
    },

    rules: {
      ...js.configs.recommended.rules,
      ...tseslint.configs.recommended.rules,
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": "warn",
    },
  },
];
