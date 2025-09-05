-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 05, 2025 at 02:10 PM
-- Server version: 8.0.30
-- PHP Version: 8.2.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `lalulintas`
--

-- --------------------------------------------------------

--
-- Table structure for table `cache`
--

CREATE TABLE `cache` (
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cache_locks`
--

CREATE TABLE `cache_locks` (
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `owner` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `failed_jobs`
--

CREATE TABLE `failed_jobs` (
  `id` bigint UNSIGNED NOT NULL,
  `uuid` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `connection` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `queue` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `exception` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `failed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `jobs`
--

CREATE TABLE `jobs` (
  `id` bigint UNSIGNED NOT NULL,
  `queue` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `attempts` tinyint UNSIGNED NOT NULL,
  `reserved_at` int UNSIGNED DEFAULT NULL,
  `available_at` int UNSIGNED NOT NULL,
  `created_at` int UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `job_batches`
--

CREATE TABLE `job_batches` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_jobs` int NOT NULL,
  `pending_jobs` int NOT NULL,
  `failed_jobs` int NOT NULL,
  `failed_job_ids` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `options` mediumtext COLLATE utf8mb4_unicode_ci,
  `cancelled_at` int DEFAULT NULL,
  `created_at` int NOT NULL,
  `finished_at` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `migrations`
--

CREATE TABLE `migrations` (
  `id` int UNSIGNED NOT NULL,
  `migration` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `migrations`
--

INSERT INTO `migrations` (`id`, `migration`, `batch`) VALUES
(1, '0001_01_01_000000_create_users_table', 1),
(2, '0001_01_01_000001_create_cache_table', 1),
(3, '0001_01_01_000002_create_jobs_table', 1),
(4, '2025_09_05_063250_vehicle_detections', 1);

-- --------------------------------------------------------

--
-- Table structure for table `password_reset_tokens`
--

CREATE TABLE `password_reset_tokens` (
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `token` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint UNSIGNED DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_activity` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `sessions`
--

INSERT INTO `sessions` (`id`, `user_id`, `ip_address`, `user_agent`, `payload`, `last_activity`) VALUES
('HXzrP5uaLwMjfrXqHEGswOjLynfk4oP2RYSwOc9b', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0', 'YTozOntzOjY6Il90b2tlbiI7czo0MDoiTGpJMmpOdFN0R2QzeVczM0dmZVo2Q0cwdU5xd1p0WTU0ZUNDbFlBaSI7czo5OiJfcHJldmlvdXMiO2E6MTp7czozOiJ1cmwiO3M6MzY6Imh0dHA6Ly8xMjcuMC4wLjE6ODAwMC9kYXNoYm9hcmQvZGF0YSI7fXM6NjoiX2ZsYXNoIjthOjI6e3M6Mzoib2xkIjthOjA6e31zOjM6Im5ldyI7YTowOnt9fX0=', 1757072304);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint UNSIGNED NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email_verified_at` timestamp NULL DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remember_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vehicle_detections`
--

CREATE TABLE `vehicle_detections` (
  `id` bigint UNSIGNED NOT NULL,
  `vehicle_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `speed` decimal(5,1) DEFAULT NULL,
  `detected_at` timestamp NOT NULL,
  `location` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Bengkalis Traffic Cam',
  `confidence` decimal(3,2) NOT NULL DEFAULT '0.00',
  `track_id` int DEFAULT NULL,
  `additional_data` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `vehicle_detections`
--

INSERT INTO `vehicle_detections` (`id`, `vehicle_type`, `speed`, `detected_at`, `location`, `confidence`, `track_id`, `additional_data`, `created_at`, `updated_at`) VALUES
(1, 'Mobil', 0.0, '2025-09-05 07:19:37', 'Bengkalis Traffic Cam', 0.86, 1, NULL, '2025-09-05 00:19:41', '2025-09-05 00:19:41'),
(2, 'Motor', 0.0, '2025-09-05 07:19:41', 'Bengkalis Traffic Cam', 0.52, 3, NULL, '2025-09-05 00:19:43', '2025-09-05 00:19:43'),
(3, 'Motor', 0.0, '2025-09-05 07:19:43', 'Bengkalis Traffic Cam', 0.81, 4, NULL, '2025-09-05 00:19:46', '2025-09-05 00:19:46'),
(4, 'Motor', 0.0, '2025-09-05 07:19:47', 'Bengkalis Traffic Cam', 0.52, 9, NULL, '2025-09-05 00:19:49', '2025-09-05 00:19:49'),
(5, 'Motor', 0.0, '2025-09-05 07:19:53', 'Bengkalis Traffic Cam', 0.75, 14, NULL, '2025-09-05 00:19:55', '2025-09-05 00:19:55'),
(6, 'Motor', 0.0, '2025-09-05 07:20:11', 'Bengkalis Traffic Cam', 0.82, 29, NULL, '2025-09-05 00:20:13', '2025-09-05 00:20:13'),
(7, 'Motor', 0.0, '2025-09-05 07:20:17', 'Bengkalis Traffic Cam', 0.82, 33, NULL, '2025-09-05 00:20:20', '2025-09-05 00:20:20'),
(8, 'Motor', 0.0, '2025-09-05 07:20:40', 'Bengkalis Traffic Cam', 0.55, 50, NULL, '2025-09-05 00:20:42', '2025-09-05 00:20:42'),
(9, 'Motor', 0.0, '2025-09-05 07:21:06', 'Bengkalis Traffic Cam', 0.70, 64, NULL, '2025-09-05 00:21:08', '2025-09-05 00:21:08'),
(10, 'Motor', 0.0, '2025-09-05 07:21:09', 'Bengkalis Traffic Cam', 0.75, 62, NULL, '2025-09-05 00:21:11', '2025-09-05 00:21:11'),
(11, 'Motor', 0.0, '2025-09-05 07:21:16', 'Bengkalis Traffic Cam', 0.54, 80, NULL, '2025-09-05 00:21:18', '2025-09-05 00:21:18'),
(12, 'Mobil', 0.0, '2025-09-05 07:21:22', 'Bengkalis Traffic Cam', 0.62, 86, NULL, '2025-09-05 00:21:24', '2025-09-05 00:21:24'),
(13, 'Motor', 0.0, '2025-09-05 07:21:41', 'Bengkalis Traffic Cam', 0.60, 99, NULL, '2025-09-05 00:21:44', '2025-09-05 00:21:44'),
(14, 'Motor', 0.0, '2025-09-05 07:21:56', 'Bengkalis Traffic Cam', 0.57, 115, NULL, '2025-09-05 00:21:59', '2025-09-05 00:21:59'),
(15, 'Motor', 0.0, '2025-09-05 07:22:16', 'Bengkalis Traffic Cam', 0.56, 135, NULL, '2025-09-05 00:22:19', '2025-09-05 00:22:19'),
(16, 'Mobil', 0.0, '2025-09-05 07:23:57', 'Bengkalis Traffic Cam', 0.85, 141, NULL, '2025-09-05 00:23:59', '2025-09-05 00:23:59'),
(17, 'Motor', 0.0, '2025-09-05 07:23:59', 'Bengkalis Traffic Cam', 0.81, 144, NULL, '2025-09-05 00:24:01', '2025-09-05 00:24:01'),
(18, 'Motor', 0.0, '2025-09-05 07:24:04', 'Bengkalis Traffic Cam', 0.52, 149, NULL, '2025-09-05 00:24:06', '2025-09-05 00:24:06'),
(19, 'Motor', 0.0, '2025-09-05 07:24:09', 'Bengkalis Traffic Cam', 0.75, 154, NULL, '2025-09-05 00:24:11', '2025-09-05 00:24:11'),
(20, 'Motor', 0.0, '2025-09-05 07:24:29', 'Bengkalis Traffic Cam', 0.82, 169, NULL, '2025-09-05 00:24:31', '2025-09-05 00:24:31'),
(21, 'Motor', 0.0, '2025-09-05 07:24:35', 'Bengkalis Traffic Cam', 0.82, 173, NULL, '2025-09-05 00:24:37', '2025-09-05 00:24:37'),
(22, 'Motor', 0.0, '2025-09-05 07:25:00', 'Bengkalis Traffic Cam', 0.55, 190, NULL, '2025-09-05 00:25:03', '2025-09-05 00:25:03'),
(23, 'Motor', 0.0, '2025-09-05 07:25:26', 'Bengkalis Traffic Cam', 0.70, 204, NULL, '2025-09-05 00:25:28', '2025-09-05 00:25:28'),
(24, 'Motor', 0.0, '2025-09-05 07:25:29', 'Bengkalis Traffic Cam', 0.75, 202, NULL, '2025-09-05 00:25:31', '2025-09-05 00:25:31'),
(25, 'Motor', 0.0, '2025-09-05 07:25:36', 'Bengkalis Traffic Cam', 0.54, 220, NULL, '2025-09-05 00:25:38', '2025-09-05 00:25:38'),
(26, 'Mobil', 0.0, '2025-09-05 07:25:42', 'Bengkalis Traffic Cam', 0.62, 226, NULL, '2025-09-05 00:25:44', '2025-09-05 00:25:44'),
(27, 'Motor', 0.0, '2025-09-05 07:26:02', 'Bengkalis Traffic Cam', 0.60, 239, NULL, '2025-09-05 00:26:04', '2025-09-05 00:26:04'),
(28, 'Motor', 0.0, '2025-09-05 07:26:16', 'Bengkalis Traffic Cam', 0.57, 255, NULL, '2025-09-05 00:26:18', '2025-09-05 00:26:18'),
(29, 'Motor', 0.0, '2025-09-05 07:26:36', 'Bengkalis Traffic Cam', 0.56, 275, NULL, '2025-09-05 00:26:38', '2025-09-05 00:26:38'),
(30, 'Mobil', 0.0, '2025-09-05 07:23:57', 'Bengkalis Traffic Cam', 0.85, 141, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(31, 'Motor', 0.0, '2025-09-05 07:23:59', 'Bengkalis Traffic Cam', 0.81, 144, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(32, 'Motor', 0.0, '2025-09-05 07:24:04', 'Bengkalis Traffic Cam', 0.52, 149, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(33, 'Motor', 0.0, '2025-09-05 07:24:09', 'Bengkalis Traffic Cam', 0.75, 154, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(34, 'Motor', 0.0, '2025-09-05 07:24:29', 'Bengkalis Traffic Cam', 0.82, 169, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(35, 'Motor', 0.0, '2025-09-05 07:24:35', 'Bengkalis Traffic Cam', 0.82, 173, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(36, 'Motor', 0.0, '2025-09-05 07:25:00', 'Bengkalis Traffic Cam', 0.55, 190, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(37, 'Motor', 0.0, '2025-09-05 07:25:26', 'Bengkalis Traffic Cam', 0.70, 204, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(38, 'Motor', 0.0, '2025-09-05 07:25:29', 'Bengkalis Traffic Cam', 0.75, 202, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(39, 'Motor', 0.0, '2025-09-05 07:25:36', 'Bengkalis Traffic Cam', 0.54, 220, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(40, 'Mobil', 0.0, '2025-09-05 07:25:42', 'Bengkalis Traffic Cam', 0.62, 226, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(41, 'Motor', 0.0, '2025-09-05 07:26:02', 'Bengkalis Traffic Cam', 0.60, 239, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(42, 'Motor', 0.0, '2025-09-05 07:26:16', 'Bengkalis Traffic Cam', 0.57, 255, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(43, 'Motor', 0.0, '2025-09-05 07:26:36', 'Bengkalis Traffic Cam', 0.56, 275, NULL, '2025-09-05 00:27:46', '2025-09-05 00:27:46'),
(44, 'Mobil', 0.0, '2025-09-05 10:17:04', 'Bengkalis Traffic Cam', 0.86, 1, NULL, '2025-09-05 03:17:07', '2025-09-05 03:17:07'),
(45, 'Motor', 0.0, '2025-09-05 10:17:07', 'Bengkalis Traffic Cam', 0.52, 3, NULL, '2025-09-05 03:17:10', '2025-09-05 03:17:10'),
(46, 'Motor', 0.0, '2025-09-05 10:17:10', 'Bengkalis Traffic Cam', 0.81, 4, NULL, '2025-09-05 03:17:13', '2025-09-05 03:17:13'),
(47, 'Motor', 0.0, '2025-09-05 10:17:14', 'Bengkalis Traffic Cam', 0.52, 9, NULL, '2025-09-05 03:17:17', '2025-09-05 03:17:17'),
(48, 'Motor', 0.0, '2025-09-05 10:17:22', 'Bengkalis Traffic Cam', 0.75, 14, NULL, '2025-09-05 03:17:24', '2025-09-05 03:17:24'),
(49, 'Motor', 0.0, '2025-09-05 10:17:40', 'Bengkalis Traffic Cam', 0.82, 29, NULL, '2025-09-05 03:17:42', '2025-09-05 03:17:42'),
(50, 'Motor', 0.0, '2025-09-05 10:17:46', 'Bengkalis Traffic Cam', 0.82, 33, NULL, '2025-09-05 03:17:48', '2025-09-05 03:17:48'),
(51, 'Motor', 0.0, '2025-09-05 10:18:09', 'Bengkalis Traffic Cam', 0.55, 50, NULL, '2025-09-05 03:18:12', '2025-09-05 03:18:12'),
(52, 'Motor', 0.0, '2025-09-05 10:25:52', 'Bengkalis Traffic Cam', 0.59, 1, NULL, '2025-09-05 03:25:55', '2025-09-05 03:25:55'),
(53, 'Motor', 0.0, '2025-09-05 10:25:55', 'Bengkalis Traffic Cam', 0.53, 3, NULL, '2025-09-05 03:25:58', '2025-09-05 03:25:58'),
(54, 'Bus', 0.0, '2025-09-05 10:25:58', 'Bengkalis Traffic Cam', 0.56, 4, NULL, '2025-09-05 03:26:00', '2025-09-05 03:26:00'),
(55, 'Motor', 0.0, '2025-09-05 10:26:07', 'Bengkalis Traffic Cam', 0.55, 24, NULL, '2025-09-05 03:26:10', '2025-09-05 03:26:10'),
(56, 'Motor', 0.0, '2025-09-05 10:26:10', 'Bengkalis Traffic Cam', 0.58, 25, NULL, '2025-09-05 03:26:13', '2025-09-05 03:26:13'),
(57, 'Truk', 0.0, '2025-09-05 10:26:14', 'Bengkalis Traffic Cam', 0.70, 28, NULL, '2025-09-05 03:26:17', '2025-09-05 03:26:17'),
(58, 'Motor', 0.0, '2025-09-05 10:26:17', 'Bengkalis Traffic Cam', 0.50, 29, NULL, '2025-09-05 03:26:19', '2025-09-05 03:26:19'),
(59, 'Motor', 0.0, '2025-09-05 10:26:23', 'Bengkalis Traffic Cam', 0.72, 37, NULL, '2025-09-05 03:26:26', '2025-09-05 03:26:26'),
(60, 'Motor', 0.0, '2025-09-05 10:26:28', 'Bengkalis Traffic Cam', 0.51, 42, NULL, '2025-09-05 03:26:31', '2025-09-05 03:26:31'),
(61, 'Bus', 0.0, '2025-09-05 10:26:36', 'Bengkalis Traffic Cam', 0.54, 4, NULL, '2025-09-05 03:26:38', '2025-09-05 03:26:38'),
(62, 'Motor', 0.0, '2025-09-05 10:26:39', 'Bengkalis Traffic Cam', 0.53, 42, NULL, '2025-09-05 03:26:42', '2025-09-05 03:26:42'),
(63, 'Motor', 0.0, '2025-09-05 10:26:43', 'Bengkalis Traffic Cam', 0.57, 45, NULL, '2025-09-05 03:26:45', '2025-09-05 03:26:45'),
(64, 'Motor', 0.0, '2025-09-05 10:26:45', 'Bengkalis Traffic Cam', 0.64, 47, NULL, '2025-09-05 03:26:48', '2025-09-05 03:26:48'),
(65, 'Motor', 0.0, '2025-09-05 10:26:50', 'Bengkalis Traffic Cam', 0.56, 48, NULL, '2025-09-05 03:26:53', '2025-09-05 03:26:53'),
(66, 'Motor', 0.0, '2025-09-05 10:27:01', 'Bengkalis Traffic Cam', 0.51, 53, NULL, '2025-09-05 03:27:03', '2025-09-05 03:27:03'),
(67, 'Motor', 0.0, '2025-09-05 10:27:05', 'Bengkalis Traffic Cam', 0.51, 29, NULL, '2025-09-05 03:27:07', '2025-09-05 03:27:07'),
(68, 'Motor', 0.0, '2025-09-05 10:27:13', 'Bengkalis Traffic Cam', 0.53, 61, NULL, '2025-09-05 03:27:16', '2025-09-05 03:27:16'),
(69, 'Motor', 0.0, '2025-09-05 10:27:21', 'Bengkalis Traffic Cam', 0.65, 70, NULL, '2025-09-05 03:27:23', '2025-09-05 03:27:23'),
(70, 'Truk', 0.0, '2025-09-05 10:27:26', 'Bengkalis Traffic Cam', 0.54, 77, NULL, '2025-09-05 03:27:28', '2025-09-05 03:27:28'),
(71, 'Motor', 0.0, '2025-09-05 10:27:31', 'Bengkalis Traffic Cam', 0.56, 61, NULL, '2025-09-05 03:27:33', '2025-09-05 03:27:33'),
(72, 'Bus', 0.0, '2025-09-05 10:27:33', 'Bengkalis Traffic Cam', 0.55, 81, NULL, '2025-09-05 03:27:36', '2025-09-05 03:27:36'),
(73, 'Truk', 0.0, '2025-09-05 10:27:41', 'Bengkalis Traffic Cam', 0.55, 81, NULL, '2025-09-05 03:27:44', '2025-09-05 03:27:44'),
(74, 'Motor', 0.0, '2025-09-05 10:27:44', 'Bengkalis Traffic Cam', 0.52, 92, NULL, '2025-09-05 03:27:47', '2025-09-05 03:27:47'),
(75, 'Motor', 0.0, '2025-09-05 10:27:47', 'Bengkalis Traffic Cam', 0.55, 94, NULL, '2025-09-05 03:27:49', '2025-09-05 03:27:49'),
(76, 'Motor', 0.0, '2025-09-05 10:27:51', 'Bengkalis Traffic Cam', 0.51, 61, NULL, '2025-09-05 03:27:54', '2025-09-05 03:27:54'),
(77, 'Truk', 0.0, '2025-09-05 10:27:55', 'Bengkalis Traffic Cam', 0.58, 98, NULL, '2025-09-05 03:27:57', '2025-09-05 03:27:57'),
(78, 'Motor', 0.0, '2025-09-05 10:28:02', 'Bengkalis Traffic Cam', 0.53, 118, NULL, '2025-09-05 03:28:04', '2025-09-05 03:28:04'),
(79, 'Bus', 0.0, '2025-09-05 10:28:12', 'Bengkalis Traffic Cam', 0.56, 81, NULL, '2025-09-05 03:28:14', '2025-09-05 03:28:14'),
(80, 'Mobil', 0.0, '2025-09-05 10:28:14', 'Bengkalis Traffic Cam', 0.57, 135, NULL, '2025-09-05 03:28:17', '2025-09-05 03:28:17'),
(81, 'Motor', 0.0, '2025-09-05 10:28:21', 'Bengkalis Traffic Cam', 0.53, 145, NULL, '2025-09-05 03:28:23', '2025-09-05 03:28:23'),
(82, 'Motor', 0.0, '2025-09-05 10:28:24', 'Bengkalis Traffic Cam', 0.58, 152, NULL, '2025-09-05 03:28:27', '2025-09-05 03:28:27'),
(83, 'Motor', 0.0, '2025-09-05 10:28:31', 'Bengkalis Traffic Cam', 0.53, 159, NULL, '2025-09-05 03:28:33', '2025-09-05 03:28:33'),
(84, 'Bus', 0.0, '2025-09-05 10:28:36', 'Bengkalis Traffic Cam', 0.61, 81, NULL, '2025-09-05 03:28:39', '2025-09-05 03:28:39'),
(85, 'Mobil', 0.0, '2025-09-05 10:28:39', 'Bengkalis Traffic Cam', 0.52, 165, NULL, '2025-09-05 03:28:42', '2025-09-05 03:28:42'),
(86, 'Motor', 0.0, '2025-09-05 10:28:44', 'Bengkalis Traffic Cam', 0.72, 171, NULL, '2025-09-05 03:28:47', '2025-09-05 03:28:47'),
(87, 'Motor', 0.0, '2025-09-05 10:28:50', 'Bengkalis Traffic Cam', 0.65, 180, NULL, '2025-09-05 03:28:52', '2025-09-05 03:28:52'),
(88, 'Motor', 0.0, '2025-09-05 10:28:56', 'Bengkalis Traffic Cam', 0.52, 190, NULL, '2025-09-05 03:28:58', '2025-09-05 03:28:58'),
(89, 'Motor', 0.0, '2025-09-05 10:28:59', 'Bengkalis Traffic Cam', 0.51, 188, NULL, '2025-09-05 03:29:01', '2025-09-05 03:29:01'),
(90, 'Mobil', 0.0, '2025-09-05 10:29:03', 'Bengkalis Traffic Cam', 0.66, 192, NULL, '2025-09-05 03:29:05', '2025-09-05 03:29:05'),
(91, 'Mobil', 0.0, '2025-09-05 10:29:09', 'Bengkalis Traffic Cam', 0.60, 205, NULL, '2025-09-05 03:29:12', '2025-09-05 03:29:12'),
(92, 'Motor', 0.0, '2025-09-05 10:29:12', 'Bengkalis Traffic Cam', 0.58, 212, NULL, '2025-09-05 03:29:14', '2025-09-05 03:29:14'),
(93, 'Truk', 0.0, '2025-09-05 10:29:16', 'Bengkalis Traffic Cam', 0.52, 218, NULL, '2025-09-05 03:29:18', '2025-09-05 03:29:18'),
(94, 'Motor', 0.0, '2025-09-05 10:29:19', 'Bengkalis Traffic Cam', 0.50, 222, NULL, '2025-09-05 03:29:21', '2025-09-05 03:29:21'),
(95, 'Truk', 0.0, '2025-09-05 10:29:26', 'Bengkalis Traffic Cam', 0.50, 81, NULL, '2025-09-05 03:29:28', '2025-09-05 03:29:28'),
(96, 'Motor', 0.0, '2025-09-05 10:29:28', 'Bengkalis Traffic Cam', 0.56, 225, NULL, '2025-09-05 03:29:31', '2025-09-05 03:29:31'),
(97, 'Motor', 0.0, '2025-09-05 10:29:31', 'Bengkalis Traffic Cam', 0.56, 179, NULL, '2025-09-05 03:29:34', '2025-09-05 03:29:34'),
(98, 'Motor', 0.0, '2025-09-05 10:29:35', 'Bengkalis Traffic Cam', 0.74, 238, NULL, '2025-09-05 03:29:37', '2025-09-05 03:29:37'),
(99, 'Mobil', 0.0, '2025-09-05 10:29:39', 'Bengkalis Traffic Cam', 0.65, 246, NULL, '2025-09-05 03:29:41', '2025-09-05 03:29:41'),
(100, 'Motor', 0.0, '2025-09-05 10:29:41', 'Bengkalis Traffic Cam', 0.75, 247, NULL, '2025-09-05 03:29:44', '2025-09-05 03:29:44'),
(101, 'Motor', 0.0, '2025-09-05 10:29:44', 'Bengkalis Traffic Cam', 0.52, 239, NULL, '2025-09-05 03:29:47', '2025-09-05 03:29:47'),
(102, 'Motor', 0.0, '2025-09-05 10:29:47', 'Bengkalis Traffic Cam', 0.52, 217, NULL, '2025-09-05 03:29:50', '2025-09-05 03:29:50'),
(103, 'Motor', 0.0, '2025-09-05 10:29:51', 'Bengkalis Traffic Cam', 0.80, 251, NULL, '2025-09-05 03:29:53', '2025-09-05 03:29:53'),
(104, 'Motor', 0.0, '2025-09-05 10:29:54', 'Bengkalis Traffic Cam', 0.54, 257, NULL, '2025-09-05 03:29:56', '2025-09-05 03:29:56'),
(105, 'Truk', 0.0, '2025-09-05 10:29:57', 'Bengkalis Traffic Cam', 0.57, 261, NULL, '2025-09-05 03:30:00', '2025-09-05 03:30:00'),
(106, 'Motor', 0.0, '2025-09-05 10:30:01', 'Bengkalis Traffic Cam', 0.74, 267, NULL, '2025-09-05 03:30:03', '2025-09-05 03:30:03'),
(107, 'Motor', 0.0, '2025-09-05 10:30:03', 'Bengkalis Traffic Cam', 0.52, 264, NULL, '2025-09-05 03:30:06', '2025-09-05 03:30:06'),
(108, 'Truk', 0.0, '2025-09-05 10:30:08', 'Bengkalis Traffic Cam', 0.56, 272, NULL, '2025-09-05 03:30:10', '2025-09-05 03:30:10'),
(109, 'Motor', 0.0, '2025-09-05 10:30:11', 'Bengkalis Traffic Cam', 0.63, 274, NULL, '2025-09-05 03:30:13', '2025-09-05 03:30:13'),
(110, 'Motor', 0.0, '2025-09-05 10:30:14', 'Bengkalis Traffic Cam', 0.66, 275, NULL, '2025-09-05 03:30:17', '2025-09-05 03:30:17'),
(111, 'Motor', 0.0, '2025-09-05 10:30:17', 'Bengkalis Traffic Cam', 0.63, 276, NULL, '2025-09-05 03:30:19', '2025-09-05 03:30:19'),
(112, 'Motor', 0.0, '2025-09-05 10:30:20', 'Bengkalis Traffic Cam', 0.72, 280, NULL, '2025-09-05 03:30:23', '2025-09-05 03:30:23'),
(113, 'Motor', 0.0, '2025-09-05 10:30:26', 'Bengkalis Traffic Cam', 0.54, 290, NULL, '2025-09-05 03:30:28', '2025-09-05 03:30:28'),
(114, 'Motor', 0.0, '2025-09-05 10:30:32', 'Bengkalis Traffic Cam', 0.73, 299, NULL, '2025-09-05 03:30:34', '2025-09-05 03:30:34'),
(115, 'Motor', 0.0, '2025-09-05 10:30:36', 'Bengkalis Traffic Cam', 0.61, 303, NULL, '2025-09-05 03:30:38', '2025-09-05 03:30:38'),
(116, 'Truk', 0.0, '2025-09-05 10:30:38', 'Bengkalis Traffic Cam', 0.61, 304, NULL, '2025-09-05 03:30:41', '2025-09-05 03:30:41'),
(117, 'Motor', 0.0, '2025-09-05 10:30:42', 'Bengkalis Traffic Cam', 0.51, 307, NULL, '2025-09-05 03:30:44', '2025-09-05 03:30:44'),
(118, 'Motor', 0.0, '2025-09-05 10:30:44', 'Bengkalis Traffic Cam', 0.53, 308, NULL, '2025-09-05 03:30:47', '2025-09-05 03:30:47'),
(119, 'Motor', 0.0, '2025-09-05 10:30:49', 'Bengkalis Traffic Cam', 0.50, 246, NULL, '2025-09-05 03:30:51', '2025-09-05 03:30:51'),
(120, 'Motor', 0.0, '2025-09-05 10:30:52', 'Bengkalis Traffic Cam', 0.69, 313, NULL, '2025-09-05 03:30:54', '2025-09-05 03:30:54'),
(121, 'Motor', 0.0, '2025-09-05 10:30:58', 'Bengkalis Traffic Cam', 0.61, 320, NULL, '2025-09-05 03:31:00', '2025-09-05 03:31:00'),
(122, 'Motor', 0.0, '2025-09-05 10:31:07', 'Bengkalis Traffic Cam', 0.53, 303, NULL, '2025-09-05 03:31:09', '2025-09-05 03:31:09'),
(123, 'Motor', 0.0, '2025-09-05 10:31:14', 'Bengkalis Traffic Cam', 0.63, 328, NULL, '2025-09-05 03:31:17', '2025-09-05 03:31:17'),
(124, 'Motor', 0.0, '2025-09-05 10:31:19', 'Bengkalis Traffic Cam', 0.67, 331, NULL, '2025-09-05 03:31:21', '2025-09-05 03:31:21'),
(125, 'Motor', 0.0, '2025-09-05 10:31:25', 'Bengkalis Traffic Cam', 0.55, 326, NULL, '2025-09-05 03:31:27', '2025-09-05 03:31:27'),
(126, 'Truk', 0.0, '2025-09-05 10:31:29', 'Bengkalis Traffic Cam', 0.52, 344, NULL, '2025-09-05 03:31:31', '2025-09-05 03:31:31'),
(127, 'Motor', 0.0, '2025-09-05 10:31:32', 'Bengkalis Traffic Cam', 0.63, 345, NULL, '2025-09-05 03:31:35', '2025-09-05 03:31:35'),
(128, 'Motor', 0.0, '2025-09-05 10:31:38', 'Bengkalis Traffic Cam', 0.57, 336, NULL, '2025-09-05 03:31:40', '2025-09-05 03:31:40'),
(129, 'Motor', 0.0, '2025-09-05 10:31:40', 'Bengkalis Traffic Cam', 0.74, 349, NULL, '2025-09-05 03:31:43', '2025-09-05 03:31:43'),
(130, 'Motor', 0.0, '2025-09-05 10:31:47', 'Bengkalis Traffic Cam', 0.61, 347, NULL, '2025-09-05 03:31:49', '2025-09-05 03:31:49'),
(131, 'Bus', 0.0, '2025-09-05 10:31:53', 'Bengkalis Traffic Cam', 0.57, 344, NULL, '2025-09-05 03:31:56', '2025-09-05 03:31:56'),
(132, 'Motor', 0.0, '2025-09-05 10:31:59', 'Bengkalis Traffic Cam', 0.52, 366, NULL, '2025-09-05 03:32:01', '2025-09-05 03:32:01'),
(133, 'Motor', 0.0, '2025-09-05 10:32:03', 'Bengkalis Traffic Cam', 0.56, 373, NULL, '2025-09-05 03:32:06', '2025-09-05 03:32:06'),
(134, 'Motor', 0.0, '2025-09-05 10:32:08', 'Bengkalis Traffic Cam', 0.69, 378, NULL, '2025-09-05 03:32:11', '2025-09-05 03:32:11'),
(135, 'Motor', 0.0, '2025-09-05 10:32:13', 'Bengkalis Traffic Cam', 0.58, 379, NULL, '2025-09-05 03:32:15', '2025-09-05 03:32:15'),
(136, 'Motor', 0.0, '2025-09-05 10:32:17', 'Bengkalis Traffic Cam', 0.53, 385, NULL, '2025-09-05 03:32:20', '2025-09-05 03:32:20'),
(137, 'Motor', 0.0, '2025-09-05 10:32:22', 'Bengkalis Traffic Cam', 0.73, 392, NULL, '2025-09-05 03:32:24', '2025-09-05 03:32:24'),
(138, 'Motor', 0.0, '2025-09-05 10:32:25', 'Bengkalis Traffic Cam', 0.57, 395, NULL, '2025-09-05 03:32:27', '2025-09-05 03:32:27'),
(139, 'Motor', 0.0, '2025-09-05 10:32:28', 'Bengkalis Traffic Cam', 0.58, 389, NULL, '2025-09-05 03:32:31', '2025-09-05 03:32:31'),
(140, 'Motor', 0.0, '2025-09-05 10:32:31', 'Bengkalis Traffic Cam', 0.51, 398, NULL, '2025-09-05 03:32:33', '2025-09-05 03:32:33'),
(141, 'Motor', 0.0, '2025-09-05 10:32:36', 'Bengkalis Traffic Cam', 0.52, 407, NULL, '2025-09-05 03:32:38', '2025-09-05 03:32:38'),
(142, 'Motor', 0.0, '2025-09-05 10:32:41', 'Bengkalis Traffic Cam', 0.61, 410, NULL, '2025-09-05 03:32:43', '2025-09-05 03:32:43'),
(143, 'Motor', 0.0, '2025-09-05 10:32:45', 'Bengkalis Traffic Cam', 0.56, 413, NULL, '2025-09-05 03:32:47', '2025-09-05 03:32:47'),
(144, 'Bus', 0.0, '2025-09-05 10:32:52', 'Bengkalis Traffic Cam', 0.51, 415, NULL, '2025-09-05 03:32:54', '2025-09-05 03:32:54'),
(145, 'Motor', 0.0, '2025-09-05 11:03:23', 'Bengkalis Traffic Cam', 0.59, 1, NULL, '2025-09-05 04:03:25', '2025-09-05 04:03:25'),
(146, 'Motor', 0.0, '2025-09-05 11:03:26', 'Bengkalis Traffic Cam', 0.53, 3, NULL, '2025-09-05 04:03:28', '2025-09-05 04:03:28'),
(147, 'Bus', 0.0, '2025-09-05 11:03:29', 'Bengkalis Traffic Cam', 0.56, 4, NULL, '2025-09-05 04:03:31', '2025-09-05 04:03:31'),
(148, 'Motor', 0.0, '2025-09-05 11:03:38', 'Bengkalis Traffic Cam', 0.55, 24, NULL, '2025-09-05 04:03:41', '2025-09-05 04:03:41'),
(149, 'Motor', 0.0, '2025-09-05 11:03:41', 'Bengkalis Traffic Cam', 0.58, 25, NULL, '2025-09-05 04:03:44', '2025-09-05 04:03:44'),
(150, 'Truk', 0.0, '2025-09-05 11:03:45', 'Bengkalis Traffic Cam', 0.70, 28, NULL, '2025-09-05 04:03:48', '2025-09-05 04:03:48'),
(151, 'Motor', 0.0, '2025-09-05 11:03:48', 'Bengkalis Traffic Cam', 0.50, 29, NULL, '2025-09-05 04:03:50', '2025-09-05 04:03:50'),
(152, 'Motor', 0.0, '2025-09-05 11:03:56', 'Bengkalis Traffic Cam', 0.72, 37, NULL, '2025-09-05 04:03:59', '2025-09-05 04:03:59'),
(153, 'Motor', 0.0, '2025-09-05 11:04:02', 'Bengkalis Traffic Cam', 0.51, 42, NULL, '2025-09-05 04:04:04', '2025-09-05 04:04:04'),
(154, 'Bus', 0.0, '2025-09-05 11:04:09', 'Bengkalis Traffic Cam', 0.54, 4, NULL, '2025-09-05 04:04:12', '2025-09-05 04:04:12'),
(155, 'Motor', 0.0, '2025-09-05 11:04:13', 'Bengkalis Traffic Cam', 0.53, 42, NULL, '2025-09-05 04:04:15', '2025-09-05 04:04:15'),
(156, 'Motor', 0.0, '2025-09-05 11:04:17', 'Bengkalis Traffic Cam', 0.57, 45, NULL, '2025-09-05 04:04:19', '2025-09-05 04:04:19'),
(157, 'Motor', 0.0, '2025-09-05 11:04:20', 'Bengkalis Traffic Cam', 0.64, 47, NULL, '2025-09-05 04:04:22', '2025-09-05 04:04:22'),
(158, 'Motor', 0.0, '2025-09-05 11:04:25', 'Bengkalis Traffic Cam', 0.56, 48, NULL, '2025-09-05 04:04:27', '2025-09-05 04:04:27'),
(159, 'Motor', 0.0, '2025-09-05 11:04:36', 'Bengkalis Traffic Cam', 0.51, 53, NULL, '2025-09-05 04:04:39', '2025-09-05 04:04:39'),
(160, 'Motor', 0.0, '2025-09-05 11:04:41', 'Bengkalis Traffic Cam', 0.51, 29, NULL, '2025-09-05 04:04:43', '2025-09-05 04:04:43');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cache`
--
ALTER TABLE `cache`
  ADD PRIMARY KEY (`key`);

--
-- Indexes for table `cache_locks`
--
ALTER TABLE `cache_locks`
  ADD PRIMARY KEY (`key`);

--
-- Indexes for table `failed_jobs`
--
ALTER TABLE `failed_jobs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `failed_jobs_uuid_unique` (`uuid`);

--
-- Indexes for table `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `jobs_queue_index` (`queue`);

--
-- Indexes for table `job_batches`
--
ALTER TABLE `job_batches`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `migrations`
--
ALTER TABLE `migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sessions_user_id_index` (`user_id`),
  ADD KEY `sessions_last_activity_index` (`last_activity`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_email_unique` (`email`);

--
-- Indexes for table `vehicle_detections`
--
ALTER TABLE `vehicle_detections`
  ADD PRIMARY KEY (`id`),
  ADD KEY `vehicle_detections_vehicle_type_index` (`vehicle_type`),
  ADD KEY `vehicle_detections_detected_at_index` (`detected_at`),
  ADD KEY `vehicle_detections_location_index` (`location`),
  ADD KEY `vehicle_detections_vehicle_type_detected_at_index` (`vehicle_type`,`detected_at`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `failed_jobs`
--
ALTER TABLE `failed_jobs`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `jobs`
--
ALTER TABLE `jobs`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `migrations`
--
ALTER TABLE `migrations`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `vehicle_detections`
--
ALTER TABLE `vehicle_detections`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=161;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
