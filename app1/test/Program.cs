// ============================================================================
// Copyright (c) 2026 Example Company
// All Rights Reserved.
//
// File: ExampleService.cs
// Description: Example source file used for testing.
// ============================================================================
namespace app1
{
    internal static class Program
    {
        /// <summary>
        ///  The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            // To customize application configuration such as set high DPI settings or default font,
            // see https://aka.ms/applicationconfiguration.
            ApplicationConfiguration.Initialize();
            Application.Run(new Form1());
        }
    }
}

// ============================================================================
// END OF FILE
// Example Company - Proprietary and Confidential
// ============================================================================