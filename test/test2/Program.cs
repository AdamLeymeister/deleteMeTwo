// -----------------------------------------------------------------------------
// ACME SOFTWARE SYSTEMS
// Internal Source Code
//
// Module: ExampleService
// Maintainer: Application Development Team
// Revision: 2.4
//
// This source code is intended solely for authorized development and testing.
// Unauthorized distribution or modification is prohibited.
// -----------------------------------------------------------------------------
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

// -----------------------------------------------------------------------------
// [ ACME SOFTWARE SYSTEMS :: END OF SOURCE ]
//
// Build Classification: INTERNAL
// Document Revision: 2.4
// -----------------------------------------------------------------------------