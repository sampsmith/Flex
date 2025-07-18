# Changelog

All notable changes to Flex001 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Flex001 Industrial Vision Inspection System
- Dual detection system for nails and board alignment
- Real-time YOLO inference with GPU acceleration
- Industrial camera integration with Basler Pylon SDK
- Hardware relay control for defect response
- SQLite database for fault logging
- PySide6-based GUI with real-time visualisation
- Modular architecture for easy maintenance and extension

### Features
- **Nail Detection**: YOLO-based nail detection with configurable confidence thresholds
- **Board Alignment**: Precise measurement of board alignment with pixel-to-mm conversion
- **Camera Management**: Support for multiple Basler cameras with hardware triggering
- **Fault Management**: Comprehensive fault logging with timestamps and measurements
- **Hardware Control**: Automatic relay triggering on defect detection
- **Settings Management**: User-friendly configuration dialog
- **Fault History**: Historical fault viewing and analysis

### Technical Details
- **Framework**: PyTorch 2.0+ with CUDA support
- **Computer Vision**: OpenCV 4.8+ for image processing
- **GUI**: PySide6 for modern Qt-based interface
- **Database**: SQLite for fault storage
- **Hardware**: Serial communication for relay control
- **Logging**: Comprehensive logging system with configurable levels

## [1.0.0] - 2025-01-XX

### Added
- Initial public release
- Complete industrial vision inspection system
- Documentation and installation guides
- GitHub repository setup with GPLv3 license

### Known Issues
- Requires commercial Basler Pylon SDK license for production use
- Ultralytics AGPL v3 dependency requires source disclosure
- Limited to Basler camera compatibility

### Future Enhancements
- Support for additional camera manufacturers
- Web-based interface for remote monitoring
- Advanced analytics and reporting features
- Integration with industrial automation systems
- Machine learning model training interface
- Multi-language support
- Docker containerisation
- Automated testing suite

---

## Version History

### Version 1.0.0
- **Release Date**: January 2025
- **Status**: Initial Release
- **License**: GNU General Public License v3 (GPLv3)
- **Compatibility**: Python 3.8+, Windows/Linux
- **Hardware**: Basler cameras, Serial relays
- **Dependencies**: PyTorch, OpenCV, PySide6, Ultralytics

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- **Phone**: Sam Smith - 07948607918
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Documentation**: Check README.md and inline code documentation 